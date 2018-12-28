# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class hr_timesheet_line(models.Model):
    _inherit = "hr.analytic.timesheet"

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if vals['name'] == '/':
            vals['name'] = self.env['project.task'].browse(
                vals['task_id']).name
        return models.Model.create(self, vals)

    @api.onchange('account_id', 'task_id')
    @api.multi
    def _change_name(self):
        for res in self:
            name = ''
            if res.account_id:
                name += res.account_id.name
            if self.task_id:
                name += ' - ' + res.task_id.name
            res.name = name
