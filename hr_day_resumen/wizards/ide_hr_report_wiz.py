# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrIdeReportWiz(models.TransientModel):
    _name="hr.ide.report.wiz"

    def _defaul_employee(self):
        user = self.env.user
        employee = self.env['hr.employee'].search([
            ('user_id', '=', user.id)])
        if employee:
            return employee[0]

    date_start = fields.Date(string="fecha inicio", required=True)
    date_end = fields.Date(string="fecha final", required=True)
    employee_id = fields.Many2one(
        string="Empleado", comodel_name="hr.employee", default=_defaul_employee)
    report_mode = fields.Selection([
        ('personal', 'Personal'),
        ('general', 'General')],
        string="Modo informe", default="personal")

    def action_wiz(self):
        for res in self:
            if res.report_mode == 'personal':
                employes = [res.employee_id]
            else:
                employes_obj = self.env['hr.employe']
                employes = employes_obj.search([('active', '=', True)])
            employe_ids = []
            for employe in employes:
                employe.report_start = res.date_start
                employe.report_end = res.date_end
                employe_ids.append(employe.id)
            action = self.env.ref(
                'hr_ide_reports.employe_report_action_ide').read()[0]
            current_domain = "[('id', 'in', " + employe_ids + ")]"
            action['domain'] = current_domain
            return action
