# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

class HrDayResumen(models.Model):
    _inherit = "hr.day.resumen"

    def get_hex_result(self, origin):
        hours = int(origin)
        minutes = int((origin*60) % 60)
        seconds = int((origin*3600) % 60)
        if minutes < 10:
            minutes = "0" + str(minutes)
        if seconds < 10:
            seconds = "0" + str(seconds)
        return str(hours) + ":" + str(minutes) + ":" + str(seconds)

    def get_hex_th(self):
        for res in self:
            return self.get_hex_result(res.teorical_hours)

    def get_hex_holi(self):
        for res in self:
            return self.get_hex_result(res.holy_hours)

    def get_hex_aus_n_j(self):
        for res in self:
            return self.get_hex_result(res.no_j_hours)

    def get_hex_aus_j(self):
        for res in self:
            return self.get_hex_result(res.j_hours)

    def get_hex_extra_hours(self):
        for res in self:
            return self.get_hex_result(res.extra_hours)

    def get_hex_h_retraso(self):
        for res in self:
            return self.get_hex_result(res.hours_delayed)