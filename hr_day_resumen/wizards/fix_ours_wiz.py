# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class HrIdeFixHours(models.TransientModel):
    _name = "hr.resumen.fix.hours"

    attendance_id = fields.Many2one(
        string="Attendanc", comodel_name="hr.attendance")
    old_hour = fields.Float(string="Horas Antiguas")
    new_hour = fields.Float(string="Horas Nuevas")

    @api.model
    def default_get(self, field_list):
        res = super(HrIdeFixHours, self).default_get(field_list)
        context = self.env.context
        assert (
            context.get("active_model") == "hr.attendance"
        ), "active_model should be payment.order"
        assert context.get("active_id"), "Missing active_id in context !"
        attendance = self.env["hr.attendance"].browse(context["active_id"])
        res.update(
            {
                "attendance_id": attendance.id,
                "old_hour": attendance.fixed_hours,
                "new_hour": attendance.fixed_hours,
            }
        )
        return res

    def action_confirm(self):
        self.attendance_id.fixed_hours = self.new_hour
        return True

class HrIdeFixHoursResumen(models.TransientModel):
    _name = "hr.resumen.fix.hours.resumen"

    resuemn_id = fields.Many2one(
        string="resumen", comodel_name="hr.day.resumen")
    old_hour = fields.Float(string="Horas Antiguas")
    new_hour = fields.Float(string="Horas Nuevas")

    @api.model
    def default_get(self, field_list):
        res = super(HrIdeFixHours, self).default_get(field_list)
        context = self.env.context
        assert (
            context.get("active_model") == "hr.day.resumen"
        ), "active_model should be payment.order"
        assert context.get("active_id"), "Missing active_id in context !"
        attendance = self.env["hr.day.resumen"].browse(context["active_id"])
        res.update(
            {
                "resumen_id": attendance.id,
                "old_hour": attendance.fixed_hours,
                "new_hour": attendance.fixed_hours,
            }
        )
        return res

    def action_confirm(self):
        self.resumen_id.fixed_hours = self.new_hour
        return True
