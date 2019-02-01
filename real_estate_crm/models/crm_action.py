# -*- encoding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.

from odoo import api, fields, models, _


class CrmAction(models.Model):
    _inherit = 'crm.action'

    top_id = fields.Many2one('real.estate.top', 'Top')

    @api.onchange('lead_id')
    def _get_top(self):
        if self.lead_id.top_id:
            self.top_id = self.lead_id.top_id
