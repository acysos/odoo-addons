# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    refrigeration_type = fields.Selection(
        string='Refrigeration type',
        selection=[('no', 'No regrigerated'), ('refri', 'refrigerated'),
                   ('fre', 'Frezee')], default='refri')

    @api.multi
    def get_sale(self, res):
        pick = self.env['stock.picking'].search([('name', '=', res.origin)])
        if pick:
            while pick:
                aux = pick
                pick = self.env['stock.picking'].search([
                    ('name', '=', pick.origin)])
        else:
            aux = res
        return self.env['sale.order'].search([('name', '=', aux.origin)])

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        sale_id = self.get_sale(res)
        if sale_id:
            res.refrigeration_type = sale_id.refrigeration_type
        else:
            res.refrigeration_type = 'no'
        return res
