# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    number_color = fields.Char(string="Number color", default="rgb(0, 0, 0)")
    background_color = fields.Char(
        string="Background color", default="rgb(250, 250, 250)")
    color_exceptions = fields.One2many(
        string="Color exceptions", comodel_name="resource.calendar.exception",
        inverse_name="calendar_id")

    def search_exception(self, resumen_id):
        ht_e = False
        b_e = False
        for exc in self.color_exceptions:
            if exc.hours_total_exception:
                ht_e = True
            if exc.begin_exception:
                b_e = True
            if ht_e and b_e:
                break;
        hours_tot = 0
        begin = resumen_id.resume_line[0].begin
        for r_line in resumen_id.resume_line:
            hours_tot += r_line.work_time
        if ht_e and b_e:
            cur_excet = self.color_exceptions.search(
                [('begin_exception', '=', begin),
                 ('hours_total_exception', '=', hours_tot),
                 ('calendar_id', '=', self.id)])
            if cur_excet:
                return cur_excet
        if b_e:
            cur_excet = self.color_exceptions.search(
                [('begin_exception', '=', begin)])
            if cur_excet:
                return cur_excet
        if ht_e:
            cur_excet = self.color_exceptions.search(
                 [('hours_total_exception', '=', hours_tot)])
            if cur_excet:
                return cur_excet
        return False

class ResourceCalendarException(models.Model):
    _name = 'resource.calendar.exception'

    name = fields.Char(string="Display name")
    calendar_id = fields.Many2one(
        string="Calendar_id", comodel_name="resource.calendar")
    number_color = fields.Char(string="Number color", default="rgb(0, 0, 0)")
    background_color = fields.Char(
        string="Background color", default="rgb(250, 250, 250)")
    hours_total_exception = fields.Float(string="Hours Total Exception")
    begin_exception = fields.Float(string="Begin Exception")
