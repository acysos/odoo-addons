# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move, partner,
                                                            inv_type)
        if move.purchase_line_id:
            res['discount1'] = move.purchase_line_id.discount1
            res['discount2'] = move.purchase_line_id.discount2
            res['discount3'] = move.purchase_line_id.discount3
        elif move.origin_returned_move_id.purchase_line_id:
            res['discount1'] = \
                move.origin_returned_move_id.purchase_line_id.discount1
            res['discount2'] = \
                move.origin_returned_move_id.purchase_line_id.discount2
            res['discount3'] = \
                move.origin_returned_move_id.purchase_line_id.discount3
        return res
