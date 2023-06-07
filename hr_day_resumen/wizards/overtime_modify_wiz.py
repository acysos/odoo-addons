# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class OvertimeModifyWiz(models.TransientModel):
    _name = 'overtime.modify.wiz'

    employee_ids = fields.Many2many(string="Empleados", comodel_name="hr.employee")
    department_ids = fields.Many2many(string="Departamentos", comodel_name="hr.department")
    reason = fields.Char(string="Motivo", required=True)
    qty = fields.Float(string="Cantidad de horas")
    date = fields.Date(string="fecha modificacion")

    @api.onchange('department_ids')
    def onchange_department(self):
        if self.department_ids:
            employees = self.env['hr.employee'].search(
                [('department_id', 'in', self.department_ids.ids)])
            self.employee_ids = [(6, 0, employees.ids)]
        else:
            self.employee_ids = [(False)]

    def action_done(self):
        overtime = self.env['hr.overtime']
        overline = self.env['hr.overtime.line']
        if self.employee_ids:
            employees = self.employee_ids
        else:
            employees = self.env['hr.employee'].search([('department_id', '!=', False)])
        for emp in employees:
            if emp.overtime_id:
                overline.create({'overtime_id': emp.overtime_id.id,
                                 'name': self.reason,
                                 'qty': self.qty,
                                 'date': self.date})
            else:
                new_over = overtime.create({'employee_id': emp.id})
                emp.overtime_id = new_over
                overline.create({'overtime_id': new_over.id,
                                 'name': self.reason,
                                 'qty': self.qty,
                                 'date': self.date})
