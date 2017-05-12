# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models


class MRP_production(models.Model):
    _inherit = 'mrp.production'

    def get_price_unit(self, move):
        if move.purchase_line_id and move.purchase_line_id.total_cost:
            if move.purchase_line_id.total_cost > move.price_unit:
                return move.purchase_line_id.total_cost
            else:
                return move.price_unit
        else:
            return move.price_unit
