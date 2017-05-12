# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    feed_machine_product_input_id = fields.Integer(
        string='Feed Machine Input ID')
    weigth = fields.Float(string='weigth')
    prov_lot = fields.Char(string='Provider lot')


class StrockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def get_prov(self):
        for res in self:
            if res.picking_id:
                res.provider = res.picking_id.partner_id

    provider = fields.Many2one(string='Supplier',comodel_name='res.partner',
                               compute=get_prov)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    feed_machine_lot = fields.Char(string='Feed Machine Related Lot')

    @api.multi
    def name_get(self):
        displayName = []
        for lot in self:
            if lot.feed_machine_lot:
                displayName.append(
                    (lot.id, lot.name + '-' +
                    lot.feed_machine_lot))
            else:
                displayName.append((lot.id, lot.name))
        return displayName

