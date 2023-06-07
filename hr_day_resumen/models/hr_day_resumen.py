# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import pytz


class HrDayResumen(models.Model):
    _name = 'hr.day.resumen'
    _order = 'day DESC'

    employee_id = fields.Many2one(
        string="Apell, Nom, Empleado", comodel_name='hr.employee',
        required=True)
    hours_per_leave = fields.Float(string="hours_per_leave")
    day = fields.Date(string="Fecha", required=True)
    attendance_ids = fields.One2many(
        string="Fichajes", comodel_name="hr.attendance",
        inverse_name="resumen_id", ondelete='cascade')
    resume_line = fields.One2many(
        comodel_name="hr.day.resumen.line", inverse_name="resumen_id")
    calendar_id = fields.Many2one(
        string="Calendario", comodel_name="resource.calendar",
        compute="get_calendar_id", store=True)
    teorical_hours = fields.Float(string="horas teoricas")
    comp_teorical_hours = fields.Char(
        string="C horas teoricas", compute="get_comp_th", store=True)
    real_hours = fields.Float(string="Horas reales")
    extra_hours = fields.Float(string="Horas extra")
    comp_extra_hours = fields.Char(
        string="C Horas extra", compute='get_comp_extra_hours', store=True)
    hours_delayed = fields.Float(string="Horas de retraso")
    comp_hours_delayed = fields.Char(
        string="C horas retraso", compute="get_comp_h_retraso", store=True)
    leave_ids = fields.Many2many(string="Ausencias", comodel_name="hr.leave")
    no_j_hours = fields.Float(string="Ausencias NO justificadas (h)")
    comp_no_j = fields.Char(string="C Aus No j", compute="get_comp_aus_n_j",
                            store=True)
    j_hours = fields.Float(string="Ausencias justificadas (h)")
    comp_j = fields.Char(string="C Aus J", compute='get_comp_aus_j', store=True)
    department_id = fields.Many2one(
        string="departamento", comodel_name="hr.department",
        compute="get_department", store=True)
    is_overtime = fields.Boolean(string="Mandar a Saldo H.E")
    overtime_id = fields.Many2one(string="Saldo", comodel_name="hr.overtime")

    _sql_constraints = [
        ('resumen_uniq', 'unique(employee_id, day)', ("Los resumenes no pueden tener mismo empleado y dia")),
    ]

    def get_prety_result(self, origin):
        if origin > 0:
            result = str(round(origin, 2)).replace('.', ',')
            if len(result) == 3:
                result = result + "0"
            return result
        else:
            return ""

    @api.depends("teorical_hours")
    def get_comp_th(self):
        for res in self:
            res.comp_teorical_hours = self.get_prety_result(res.teorical_hours)

    @api.depends("holy_hours")
    def get_comp_holi(self):
        for res in self:
            res.comp_holy_hours = self.get_prety_result(res.holy_hours)

    @api.depends("no_j_hours")
    def get_comp_aus_n_j(self):
        for res in self:
            res.comp_no_j = self.get_prety_result(res.no_j_hours)

    @api.depends("j_hours")
    def get_comp_aus_j(self):
        for res in self:
            res.comp_j = self.get_prety_result(res.j_hours)

    @api.depends("extra_hours")
    def get_comp_extra_hours(self):
        for res in self:
            res.comp_extra_hours = self.get_prety_result(res.extra_hours)

    @api.depends("hours_delayed")
    def get_comp_h_retraso(self):
        for res in self:
            res.comp_hours_delayed = self.get_prety_result(res.hours_delayed)

    @api.onchange('is_overtime')
    def change_overtime(self):
        if self.is_overtime:
            overtime = self.env['hr.overtime'].search(
                [('employee_id', '=', self.employee_id.id)])
            if not overtime:
                overtime = self.env['hr.overtime'].create(
                    {'employee_id': self.employee_id.id})
                self.employee_id.overtime_id = overtime
            self.overtime_id = overtime
        else:
            self.overtime_id = False

    @api.depends('employee_id')
    def get_department(self):
        for res in self:
            if res.employee_id:
                res.department_id = res.employee_id.department_id

    def get_leave_hours(self, leave):
        if leave.request_unit_half:
            if len(self.resume_line) > 1:
                tot_h = 0
                for line in self.resume_line:
                    tot_h += line.work_time    
                if leave.request_date_from_period == 'am':
                    return self.hours_per_leave - tot_h
                else:
                    return self.hours_per_leave - tot_h
            else:
                return self.hours_per_leave/2
        elif leave.request_unit_hours:
                return (leave.date_to - leave.date_from).total_seconds() / 3600
        else:
            return self.hours_per_leave

    def update_hours(self):
        for res in self:
            tot_th = 0
            tot_rh = 0
            tot_wh = 0
            tot_j_hours = 0
            tot_no_j_hours = 0
            leave_hours = 0
            for line in res.resume_line:
                tot_th += line.work_time
            for leave in res.leave_ids:
                if leave.state in ['validate', 'validate1']:
                    leave_hours = res.get_leave_hours(leave)
                    if leave.holiday_status_id.include_in_theoretical:
                        tot_no_j_hours += leave_hours
                    else:
                        tot_j_hours += leave_hours
                elif leave.state in ['refuse', 'draft', 'cancel']:
                    res.leave_ids = [(3, leave.id)]
            res.j_hours = tot_j_hours
            res.no_j_hours = tot_no_j_hours
            for atten in res.attendance_ids:
                tot_rh += self.get_fixed_hours(atten)
            tot_wh = tot_rh
            if tot_rh >= tot_th:
                res.extra_hours = tot_rh - tot_th
                res.hours_delayed = 0
            else:
                res.extra_hours = 0
                res.hours_delayed = tot_th - tot_rh
            res.teorical_hours = tot_th
            res.real_hours = tot_wh
            if not res.resume_line and not res.leave_ids and not res.attendance_ids:
                res.unlink()
            else:
                if res.attendance_ids or res.leave_ids:
                    if not res.is_overtime:
                        res.is_overtime = True
                        res.change_overtime()

    def get_fixed_hours(self, attendance):
        return attendance.worked_hours

    def set_transport(self, presencial, transport_type, ext_h):
        transport = False
        if presencial:
            if transport_type == 'all':
                    transport = True
            elif ext_h > 0:
                if transport_type == 'holidays':
                    transport = True
        return transport

    def change_transport(self):
        for atten in self:
            atten.is_transport = atten.is_transport != True

class HrDayResumeLine(models.Model):
    _name = 'hr.day.resumen.line'
    _order = 'begin ASC'

    resumen_id = fields.Many2one(
        string="Resume", comodel_name='hr.day.resumen')
    employee_id = fields.Many2one(string="employee", comodel_name="hr.employee")
    begin = fields.Datetime(string="Begin")
    end = fields.Datetime(string='End')
    work_time = fields.Float(string="Work Time", compute="get_work_time",
                             store=True)

    @api.depends('begin', 'end')
    def get_work_time(self):
        for res in self:
            if res.begin and res.end:
                res.work_time = (res.end - res.begin).total_seconds() / 3600
            else:
                res.work_time = 0

    def write(self, vals):
        for r_line in self:
            old_wt = r_line.work_time
            res = super(HrDayResumeLine, r_line).write(vals)
            r_line.resumen_id.update_hours()
            context = self.env.context
            if not context.get('update_hpl'):
                w_dif = r_line.work_time - old_wt
                r_line.resumen_id.hours_per_leave += w_dif
        return res

    @api.model
    def create(self, vals):
        res = super(HrDayResumeLine, self).create(vals)
        resumen = res.get_resumen(res.employee_id, res.begin)
        res.update_resumen(resumen, True)
        return res

    def get_resumen(self, employee_id, begin):
        date = fields.Date.context_today(self, begin)
        domain = [('employee_id', '=', employee_id.id),
                  ('day', '=', date)]
        return self.env['hr.day.resumen'].search(domain)

    def update_resumen(self, resumen, update):
        for res in self:
            old_resumen = res.resumen_id
            if resumen:
                resumen.resume_line = [(4, res.id)]
                resumen.hours_per_leave += res.work_time
            else:
                vals = {'day': res.begin.date(),
                        'employee_id': res.employee_id.id,
                        'resume_line': [(4, res.id)],
                        'hours_per_leave': res.work_time,
                        'calendar_id': res.employee_id.resource_calendar_id.id}
                resumen = self.env['hr.day.resumen'].create(vals)
            if old_resumen:
                if not old_resumen.attendance_ids and \
                        not old_resumen.resume_line:
                    old_resumen.unlink()
                else:
                    old_resumen.update_hours()
            if update:
                resumen.update_hours()


class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    overtime_line_id = fields.Many2one(
        string="Linea saldo", comodel_name="hr.overtime.line", delete="cascade")

    @api.model
    def create(self, vals):
        res = super(HolidaysAllocation, self).create(vals)
        if 'state' in vals.keys() and vals['state'] == 'validate' and vals['holiday_type'] == 'employee':
            res.link_overtime()
        return res

    def link_overtime(self):
        if self.holiday_status_id.is_overtime:
            if not self.overtime_line_id:
                overtime = self.employee_id.overtime_id
                if not overtime:
                    overtime = self.env['hr.overtime'].create(
                        {'employee_id': self.employee_id.id})
                    self.employee_id.overtime_id = overtime
                vals = {'overtime_id': overtime.id,
                        'name': self.name,
                        'qty': -(self.number_of_hours_display),
                        'date': fields.date.today()}
                self.overtime_line_id = self.env['hr.overtime.line'].create(vals)
            else:
                self.overtime_line_id.qty = -(self.number_of_hours_display)
        else:
            if self.overtime_line_id:
                self.overtime_line_id.unlink()

    def action_draft(self):
        res = super(HolidaysAllocation, self).action_draft()
        if self.overtime_line_id:
            self.overtime_line_id.unlink()
        return res

    def action_confirm(self):
        res = super(HolidaysAllocation, self).action_confirm()
        self.link_overtime()
        return res

    def action_approve(self):
        res = super(HolidaysAllocation, self).action_approve()
        self.link_overtime()
        return res

    def action_validate(self):
        res = super(HolidaysAllocation, self).action_validate()
        if len(self):
            self.link_overtime()
        return res

    def action_refuse(self):
        res = super(HolidaysAllocation, self).action_refuse()
        if self.overtime_line_id:
            self.overtime_line_id.unlink()
        return res


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_overtime = fields.Boolean(string="Compensacion H.extra")
    include_in_theoretical = fields.Boolean(string="Recuperables")


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    day_resumen_ids = fields.Many2many(
        string="Resumenes", comodel_name="hr.day.resumen")
    is_overtime = fields.Boolean(string="Compensacion H.extra")
    action_url = fields.Char(string="url", compute="get_url")
    last_mail_date = fields.Datetime(
        string="ultimo mail")

    def update_resumen_hours(self, leave):
        for resumen in leave.day_resumen_ids:
                resumen.update_hours()

    def unlink(self):
        for res in self:
            if res.state in ['confirm', 'validate', 'validate1']:
                raise ValidationError(
                    'Primero cancela o rechaza la ausencia')
        return super(HrLeave, self).unlink()

    def action_draft(self):
        result = super(HrLeave, self).action_draft()
        for res in self:
            res.sudo().update_resumen_hours(res)
        return result

    def action_refuse(self):
        result = super(HrLeave, self).action_refuse()
        for res in self:
            res.sudo().update_resumen_hours(res)
        return result

    def link_resumen_ids(self, res):
        if res.holiday_type != 'employee':
            return True
        if res.request_unit_half or res.request_unit_hours:
            if res.request_unit_hours and res.request_hour_to < res.request_hour_from:
                date_end = res.request_date_from + timedelta(days=1)
                date_from = res.request_date_from + timedelta(days=1)
            else:
                date_end = res.request_date_from
                date_from = res.request_date_from
        else:
            date_end = res.request_date_to
            date_from = res.request_date_from
        resumen_ids = res.get_resumen_ids(
            res.employee_id, date_from, date_end, res.request_unit_hours,
            res.request_unit_half)
        if resumen_ids:
            res.update_resumen_ids(resumen_ids)
        else:
            raise ValidationError(
                "No se encontro horario asociado a estos dias")

    def action_validate(self):
        result = super(HrLeave, self).action_validate()
        for res in self:
            res.sudo().update_resumen_hours(res)
        return result

    def action_confirm(self):
        result = super(HrLeave, self).action_confirm()
        for res in self:
            res.sudo().link_resumen_ids(res)
        return result

    @api.model
    def create(self, vals):
        res = super(HrLeave, self).create(vals)
        if 'state' in vals.keys() and vals['state'] == 'validate' and vals['holiday_type'] == 'employee':
            res.sudo().link_resumen_ids(res)
        return res

    def action_approve(self):
        result = super(HrLeave, self).action_approve()
        for res in self:
            res.sudo().link_resumen_ids(res)
        return result

    def update_resumen_ids(self, resumen_ids):
        for resumen in resumen_ids:
            self.update_resumen(resumen, True)

    def get_resumen_ids(self, employee, date_start, date_end, unit_hours, unit_half):
        resumen_obj = self.env['hr.day.resumen']
        resumen_ids = resumen_obj.search([
            ('employee_id', '=', employee.id),
            ('day', '>=', date_start), ('day', '<=', date_end)])
        if not resumen_ids:
            resumen_ids = []
            while date_start <= date_end:
                if date_start.weekday() < 5 or unit_half or unit_hours:
                    vals = {'day': date_start, 'employee_id': employee.id}
                    resumen_ids.append(resumen_obj.create(vals))
                date_start = date_start + timedelta(days=1)
        return resumen_ids

    def update_resumen(self, resumen, update):
        for res in self:
            resumen.leave_ids = [(4, res.id)]
            context = self.env.context.copy()
            context['update_hpl'] = True
            if not res.request_unit_half and not res.request_unit_hours:
                for line in resumen.resume_line:
                    line.with_context(context).unlink()
            else:
                date_from = res.date_from
                date_end = res.date_to
                for rline in resumen.resume_line:
                    if rline.begin <= date_from and rline.end > date_from:
                        if rline.begin == date_from:
                            if rline.end < date_end:
                                rline.with_context(context).unlink()
                            else:
                                rline.with_context(context).write(
                                    {'begin': date_end})
                        elif rline.end == date_end:
                            rline.with_context(context).write(
                                    {'end': date_from})
                        else:
                            aux_end = rline.end
                            rline.with_context(context).write(
                                    {'end': date_from})
                            new_day = self.env['hr.day.resumen.line'].create(
                                    {'resumen_id': resumen.id,
                                     'employee_id': resumen.employee_id.id,
                                     'begin': date_end,
                                     'end': aux_end,
                                })
                            new_day.resumen_id.hours_per_leave -= new_day.work_time
                            resumen.day_hour_ids = [(4, new_day.id)]
                    elif rline.begin < date_end and rline.end >= date_end:
                        rline.begin = date_end
            if update:
                resumen.update_hours()

class HrAttendance(models.Model):
    _name = 'hr.attendance' 
    _inherit = ['mail.thread', 'hr.attendance']


    def _default_employee(self):
        if self._context.get('default_model') == 'day.resumen':
            resumen = self.env['hr.day.resumen'].browse(self._context.get('default_resumen'))
            if resumen:
                print(resumen)
                print(resumen.employee_id)
                return resumen.employee_id
        return super(HrAttendance, self)._default_employee()

    employee_id = fields.Many2one(
        'hr.employee', string="Employee", default=_default_employee,
        required=True, ondelete='cascade', index=True)
    resumen_id = fields.Many2one(
        string="Resumen dia", comodel_name='hr.day.resumen')
    day = fields.Date(string="Attendance Day", compute="get_att_day", store=True)

    def unlink(self):
        resumen = self.resumen_id
        result = super(HrAttendance, self).unlink()
        resumen.update_hours()
        return result

    @api.model
    def create(self, vals):
        res = super(HrAttendance, self).create(vals)
        if 'check_out' in vals.keys() and 'employee_id' in vals.keys() and vals['check_out']:
            resumen = res.get_resumen(res.employee_id, res.check_out)
            res.update_resumen(resumen, True)
        return res

    def write(self, vals):
        res = super(HrAttendance, self).write(vals)
        if 'employee_id' in vals.keys():
            raise ValidationError(
                "No se puede cambiar el empleado de una asistencia, porfabor elimine esta y cree una nueva con los datos correctos")
        if 'check_in' in vals.keys() or 'check_out' in vals.keys():
            for atten in self:
                if atten.check_out:
                    resumen = atten.get_resumen(atten.employee_id, atten.check_out)
                    atten.update_resumen(resumen, True)
        return res

    def get_resumen(self, employee_id, check_out):
        date = fields.Date.context_today(self, check_out)
        domain = [('employee_id', '=', employee_id.id),
                  ('day', '=', date)]
        return self.env['hr.day.resumen'].search(domain)

    @api.depends('check_out')
    def get_att_day(self):
        for res in self:
            if res.check_out:
                res.day = date = fields.Date.context_today(self, res.check_out)

    def update_resumen(self, resumen, update):
        for res in self:
            old_resumen = res.resumen_id
            if resumen:
                resumen.attendance_ids = [(4, res.id)]
            else:
                date = fields.Date.context_today(self, res.check_out)
                vals = {'day': date,
                        'employee_id': res.employee_id.id,
                        'attendance_ids': [(4, res.id)]}
                resumen = self.env['hr.day.resumen'].create(vals)
            if old_resumen:
                if not old_resumen.attendance_ids and \
                        not old_resumen.resume_line:
                    old_resumen.unlink()
                else:
                    old_resumen.update_hours()
            if update:
                resumen.update_hours()
