# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.picking'

    feed_machine_product_input_id = fields.Integer(
        string='Feed Machine Input ID')


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    feed_machine_lot = fields.Char(string='Feed Machine Related Lot')

