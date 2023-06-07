# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from datetime import datetime, timedelta
import pytz


class UpdateCalendarWiz(models.TransientModel):
    _name = 'update.calendar.wiz'

    employee_ids = fields.Many2many(
        comodel_name="hr.employee", string="employees")
    calendar_id = fields.Many2one(comodel_name="resource.calendar", string="Nuevo calendario")
    start_date = fields.Date(
        string='Start', default=fields.Date.today())
    end_date = fields.Date(
        string='Start', default=fields.Date.today())

    def action_confirm(self):
        domain = [('resource_calendar_id', '!=', False)]
        if self.employee_ids:
            employees = []
            for employee in self.employee_ids:
                employees.append(employee.id)
            domain.append(('id', 'in', employees))
        employees_obj = self.env['hr.employee'].search(domain)
        day = self.start_date
        public_holidays = self.env['hr.holidays.public.line'].search([
            ('date', '<=', self.end_date),
            ('date', '>=', self.start_date)])
        public_holidays_days = []
        for holi in public_holidays:
            public_holidays_days.append(holi.date)
        while day <= self.end_date:
            for emp in employees_obj:
                old_resu = self.env['hr.day.resumen'].search(
                    [('employee_id', '=', emp.id), ('day', '=', day)])
                for old in old_resu:
                    for oline in old.resume_line:
                        oline.unlink()
                    old.update_hours()
                    old.hours_per_leave = 0
                if day not in public_holidays_days:
                    self.create_resume_lines(emp, day, self.calendar_id)
                else:
                    public_holiday = self.env['hr.holidays.public.line'].search(
                        [('date', '=', day)])
                    emp_s = emp.address_id.state_id
                    if public_holiday.state_ids and emp_s.id not in public_holiday.state_ids.ids:
                        self.create_resume_lines(emp, day, self.calendar_id)
                old_atten = self.env['hr.attendance'].search([
                    ('employee_id', '=', emp.id), ('day', '=', day)])
                resu = False
                for atten in old_atten:
                    if not resu:
                        resu = self.env['hr.day.resumen'].search(
                        [('employee_id', '=', emp.id), ('day', '=', day)])
                    atten.update_resumen(resu, True)
                old_leave = self.env['hr.leave'].search(
                    [('employee_id', '=', emp.id),
                    ('request_date_to', '>=', day),
                    ('request_date_from', '<=', day)])
                for leave in old_leave:
                    if not resu:
                        resu = self.env['hr.day.resumen'].search(
                            [('employee_id', '=', emp.id), ('day', '=', day)])
                    leave.update_resumen(resu, True)
            day = day + timedelta(days=1)

    def create_resume_lines(self, emp, day, calendar_id):
        if calendar_id:
            calendar = calendar_id
        else:
            calendar = emp.resource_calendar_id
        for c_atten in calendar.attendance_ids: 
            if not c_atten.date_from or c_atten.date_from <= day <= c_atten.date_to:
                if str(day.weekday()) == c_atten.dayofweek:
                    vals = self.get_day_vals(day, c_atten, emp)
                    new_line = self.env['hr.day.resumen.line'].create(vals)
                    if self.calendar_id:
                        new_line.resumen_id.calendar_id = calendar_id

    def get_day_vals(self, day, c_atten, emp):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        h_f = '{0:02.0f}:{1:02.0f}'.format(*divmod(c_atten.hour_from * 60, 60))
        h_t = '{0:02.0f}:{1:02.0f}'.format(*divmod(c_atten.hour_to * 60, 60))
        d_f = local.localize(datetime.strptime(
            (str(day) + ' ' + h_f+ ':00'), '%Y-%m-%d %H:%M:%S')
            ).astimezone(pytz.timezone('UTC')).strftime(
                            '%Y-%m-%d %H:%M:%S')
        d_t = local.localize(datetime.strptime(
            (str(day) + ' ' + h_t+ ':00'), '%Y-%m-%d %H:%M:%S')
            ).astimezone(pytz.timezone('UTC')).strftime(
                            '%Y-%m-%d %H:%M:%S')
        return {'begin': d_f, 'end': d_t, 'employee_id': emp.id}


class ChangeCalendarWiz(models.TransientModel):
    _name = 'change.calendar.wiz'

    employee_id = fields.Many2one(string='Empleado', comodel_name='hr.employee')
    old_calendar = fields.Many2one(
        string="Calendario antiguo", comodel_name='resource.calendar')
    new_calendar = fields.Many2one(
        string="Calendario nuevo", comodel_name='resource.calendar')
    start_date = fields.Date(
        string='Fecha de aplicación', default=fields.Date.today())

    @api.model
    def default_get(self, field_list):
        res = super(ChangeCalendarWiz, self).default_get(field_list)
        context = self.env.context
        employee = self.env["hr.employee"].browse(context["active_id"])
        res.update(
            {
                "employee_id": employee.id,
                "old_calendar": employee.resource_calendar_id.id,
            }
        )
        return res

    def action_confirm(self):
        resumen_ids = self.env['hr.day.resumen'].search(
            [('employee_id', '=', self.employee_id.id),
             ('day', '>=', self.start_date)])
        self.employee_id.resource_calendar_id = self.new_calendar
        for resumen in resumen_ids:
            resumen.calendar_id = self.new_calendar
            control = True
            for attendance in resumen.attendance_ids:
                if not attendance.check_out:
                    control = False
            if control:
                resumen.update_hours()