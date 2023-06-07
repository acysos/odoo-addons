# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_id = fields.Many2one(
        string="Registro horas extra", comodel_name="hr.overtime")
    overtime_qty = fields.Float(string="Saldo horas extra", 
                                compute="get_overtime", store="True")

    @api.depends('overtime_id', 'overtime_id.quantity')
    def get_overtime(self):
        for res in self:
            if res.overtime_id:
                res.overtime_qty = res.overtime_id.quantity
            else:
                res.overtime_qty = 0


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    overtime_id = fields.Many2one(
        string="Registro horas extra", comodel_name="hr.overtime")
    overtime_qty = fields.Float(string="Saldo horas extra")