# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AeatSiiResult(models.Model):
    _inherit = 'aeat.sii.result'

    pos_order_id = fields.Many2one(comodel_name='pos.order',
                                   string='POS Order')

    def _prepare_vals(self, model_id, res, type, fault, model):
        vals = super(AeatSiiResult, self)._prepare_vals(
            model_id, res, type, fault, model)
        if model == 'pos.order':
            vals['pos_order_id'] = model_id.id
        return vals
