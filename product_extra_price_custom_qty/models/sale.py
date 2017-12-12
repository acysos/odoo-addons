# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class sale_order(models.Model):
    _inherit = 'sale.order'

    def prepare_expand_extra_price_vals(
            self, line, order, sequence, tax_ids):
        vals = super(sale_order, self).prepare_expand_extra_price_vals(
            line, order, sequence, tax_ids)
        vals['product_uom_qty'] = (
            line.product_id.extra_price_qty * line.product_uom_qty)
        vals['product_uos_qty'] = (
            line.product_id.extra_price_qty * line.product_uos_qty)
        return vals


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def update_child(self, line, vals):
        if 'product_uom_qty' in vals and line.extra_child_line_id:
            qty = vals['product_uom_qty'] * line.product_id.extra_price_qty
            line.extra_child_line_id.product_uom_qty = qty
