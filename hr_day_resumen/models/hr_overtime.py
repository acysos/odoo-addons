# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError

from odoo import models, fields, api

class HrOvertime(models.Model):
    _name = 'hr.overtime'

    employee_id = fields.Many2one(
        string="empleado", comodel_name="hr.employee", required=True)
    initial_qty = fields.Float(string="Saldo inicial")
    quantity = fields.Float(string="Saldo", compute="get_quantity", store="True")
    overtime_history = fields.One2many(
        string="registro", comodel_name="hr.day.resumen",
        inverse_name="overtime_id")
    overtime_modify = fields.One2many(
        string="Modificaciones", comodel_name='hr.overtime.line',
        inverse_name="overtime_id")

    @api.depends(
        'overtime_history', 'overtime_history.extra_hours','initial_qty',
        'overtime_history.no_j_hours', 'overtime_modify', 'overtime_modify.qty')
    def get_quantity(self):
        for res in self:
            qty = res.initial_qty
            for history in res.overtime_history:
                qty += history.extra_hours
                qty -= history.no_j_hours
                qty -= history.hours_delayed
            for line in res.overtime_modify:
                qty += line.qty
            res.quantity = qty


class HrOvertimeLine(models.Model):
    _name = 'hr.overtime.line'
    _order = "date"

    overtime_id = fields.Many2one(string="Saldo", comodel_name="hr.overtime")
    name = fields.Char(string="Motivo", required=True)
    qty = fields.Float("Horas")
    date = fields.Date(string="Fecha")

    def unlink(self):
        for res in self:
            allocation = self.env['hr.leave.allocation'].search(
                [('overtime_line_id', '=', res.id)])
            if allocation and allocation.state in ('confirm', 'validate', 'validate1') and allocation.holiday_status_id.is_overtime:
                raise ValidationError(
                    'Primero cancela o rechaza la asignacion de ausencia')
        return super(HrOvertimeLine, self).unlink()
