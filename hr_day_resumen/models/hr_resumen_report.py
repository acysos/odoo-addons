# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrResumenReport(models.Model):
    _name = "hr.resumen.report"
    _order = "date_start DESC"

    name = fields.Char("Nombre", requiered=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('calc', 'Calculado'),
        ('done', 'Confirmado'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False,
        index=True, default='draft')
    date_start = fields.Date(string="fecha inicio", required=True)
    date_end = fields.Date(string="fecha final", required=True)
    employee_id = fields.Many2one(
        string="Empleado", comodel_name="hr.employee")
    line_ids = fields.One2many(
        string="Lineas Informe", comodel_name="hr.resumen.report.line",
        inverse_name="report_id")


    def get_resumen_domain(self, employee, date_start, date_end):
        domain = [('employee_id', '=', employee.id),
                  ('day', '<=', date_end),
                  ('day', '>=', date_start)]
        return domain

    def get_em_domain(self, employee_id):
        domain = [('department_id', '!=', False)]
        if self.employee_id:
            domain.append(('id', '=', self.employee_id.id))
        return domain

    def get_dh_domain(self, employee, date_start, date_end):
        user_id = employee.user_id
        domain = [('user_id', '=', user_id.id), ('end', '<=', date_end),
                  ('end', '>=', date_start)]
        return domain

    def get_atten_domain(self, employee, date_start, date_end):
        domain = [('employee_id', '=', employee.id),
                  ('check_out', '<=', date_end),
                  ('check_out', '>=', date_start)]
        return domain

    def do_employee_report(self, employee):
        resumen_ids = self.get_resumen(employee, self.date_start, self.date_end)
        self.create_lines(employee, resumen_ids)

    def get_teorical_hours(self, employee):
        day_hours = self.env['day.hours.sample'].search(
            self.get_dh_domain(employee, self.date_start, self.date_end))
        return day_hours

    def get_resumen(self, employee, date_start, date_end):
        resumen_ids = self.env['hr.day.resumen'].search(
            self.get_resumen_domain(employee, date_start, date_end))
        return resumen_ids

    def get_attendances(self, employee, date_start, date_end):
        attendances = self.env['hr.attendance'].search(
            self.get_atten_domain(employee, date_start, date_end))
        return attendances

    def do_report(self):
        employees = self.env['hr.employee'].search(self.get_em_domain(
            self.employee_id))
        for employe in employees:
            self.do_employee_report(employe)

    def action_do(self):
        for res in self:
            res.do_report()
            res.state = 'calc'

    def action_done(self):
        for res in self:
            res.state = 'done'

    def action_draft(self):
        for res in self:
            for line in res.line_ids:
                line.unlink()
            res.state = "draft"

    def action_cancel(self):
        for res in self:
            res.state = "cancel"


    def get_report_vals(self, employee, resumen_ids):
        j_hours = 0
        no_j_hours = 0
        tot_t_w_h = 0
        work_time = 0
        extra_hour = 0
        extra1 = 0
        extraf = 0
        hours_delayed = 0
        work_days = 0
        overtime_dif = 0
        for resumen in resumen_ids:
            if resumen.attendance_ids:
                work_days += 1
            if resumen.is_overtime:
                overtime_dif += resumen.extra_hours
                overtime_dif -= resumen.j_hours
                overtime_dif -= resumen.no_j_hours
            j_hours += resumen.j_hours
            no_j_hours += resumen.no_j_hours
            work_time += resumen.real_hours
            extra_hour += resumen.extra_hours
            if not resumen.is_overtime:
                if resumen.teorical_hours > 0:
                    extra1 += resumen.extra_hours
                else:
                    extraf += resumen.extra_hours
            hours_delayed += resumen.hours_delayed
            tot_t_w_h += resumen.teorical_hours
        vals = {'report_id': self.id,
                'employee_id': employee.id,
                'teorycal_hour': tot_t_w_h,
                'worked_hours': work_time,
                'worked_days': work_days,
                'extra_hour': extra_hour,
                'extra_1': extra1,
                'extra_f': extraf,
                'hours_delayed': hours_delayed,
                'j_hours': j_hours,
                'no_j_hours': no_j_hours,
                'overtime_dif': overtime_dif}
        return vals

    def create_lines(self, employee, resumen_ids):
        report_line_obj = self.env['hr.resumen.report.line']
        vals = self.get_report_vals(employee, resumen_ids)
        report_line_obj.create(vals)



class HrIdeReportLine(models.Model):
    _name = 'hr.resumen.report.line'

    report_id = fields.Many2one(string="Informe", comodel_name="hr.resumen.report")
    employee_id = fields.Many2one(
        string="Apell, Nom, Empleado", comodel_name='hr.employee')
    teorycal_hour = fields.Float(string='Horas teoricas')
    worked_hours = fields.Float(string='Horas trabajadas')
    worked_days = fields.Integer(string="Días trabajados")
    hours_delayed = fields.Float(string="Horas de retraso")
    j_hours = fields.Float(string="Ausencias justificadas (h)")
    no_j_hours = fields.Float(string="Ausencias no justificadas (h)")
    extra_hour = fields.Float(string="Horas extra")
    extra_1 = fields.Float(string="extra tipo 1")
    extra_f = fields.Float(string="extra festivo")
    overtime_dif = fields.Float(string='Cambio saldo H. extra')

    def open_teorycal_hour_lines(self):
        for res in self:
            t_w_h = res.report_id.get_teorical_hours(res.employee_id)
            action = self.env.ref(
                'hr_ide_reports.day_hours_sample_action_resume').read()[0]
            current_domain = "[('id', 'in', " + str(t_w_h.ids) + ")]"
            action['domain'] = current_domain
            return action

    def open_resumen(self):
        for res in self:
            resumen = res.report_id.get_resumen(
                res.employee_id, res.report_id.date_start,
                res.report_id.date_end                                                )
            action = self.env.ref(
                'hr_day_resumen.hr_day_resumen_action_resume').read()[0]
            current_domain = "[('id', 'in', " + str(resumen.ids) + ")]"
            action['domain'] = current_domain
            return action

    def open_work_hours(self):
        for res in self:
            action = self.env.ref(
                'hr_ide_reports.attendance_action_resume').read()[0]
            current_domain = res.report_id.get_atten_domain(
                res.employee_id, res.report_id.date_start,
                res.report_id.date_end)
            action['domain'] = current_domain
            return action

