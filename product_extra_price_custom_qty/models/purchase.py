# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2017  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def prepare_expand_extra_prices(
                self, line, tax_ids, extra_price, order, sequence):
        vals = super(PurchaseOrder, self).prepare_expand_extra_prices(
            line, tax_ids, extra_price, order, sequence)
        vals['product_qty'] = (
            line.product_id.extra_price_qty * line.product_qty)
        return vals


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def update_child(self, line, vals):
        if 'product_qty' in vals and line.extra_child_line_id:
            qty = vals['product_qty'] * line.product_id.extra_price_qty
            line.extra_child_line_id.product_qty = qty
