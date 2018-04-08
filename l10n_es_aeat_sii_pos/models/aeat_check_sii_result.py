# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AeatCheckSiiResult(models.Model):
    _inherit = 'aeat.check.sii.result'

    pos_order_id = fields.Many2one(comodel_name='pos.order',
                                   string='POS Order')

    def _get_data(self, model_id, res, model):
        data, key, key_type = super(AeatCheckSiiResult, self)._get_data(
            model_id, res, model)
        if model == 'pos.order':
            data = res['RegistroRespuestaConsultaLRFacturasEmitidas'][0]
            key = 'DatosFacturaEmitida'
            key_type = 'sale'
        return data, key, key_type

    def _prepare_vals(self, model_id, res, fault, model):
        vals = super(AeatCheckSiiResult, self)._prepare_vals(
            model_id, res, fault, model)
        if model == 'pos.order':
            vals['pos_order_id'] = model_id.id
        return vals
