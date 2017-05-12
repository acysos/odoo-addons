# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models


class MRP_production(models.Model):
    _inherit = 'mrp.production'

    def get_price_unit(self, move):
        if move.purchase_line_id and move.purchase_line_id.total_cost:
            trans_cost = move.purchase_line_id.total_cost - move.price_unit
            return self.get_price(move, trans_cost)
        else:
            return self.get_price(move, 0)

    def get_price(self, move, trans_cost):
        for q in move.quant_ids:
            lot = q.lot_id
            if lot.unit_cost and lot.unit_cost > 0:
                return lot.unit_cost + trans_cost
            else:
                return move.price_unit + trans_cost
