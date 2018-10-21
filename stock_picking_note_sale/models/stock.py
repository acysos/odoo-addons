# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id:
            sale_order = self.sale_line_id.order_id
            res['note'] = sale_order.note and sale_order.note or ''
        return res
