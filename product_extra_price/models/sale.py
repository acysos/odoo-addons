# -*- coding: utf-8 -*-
# Copyright 2019 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2019 Alexander Ezquebo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    extra_parent_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Extra Price',
        help='The line that contain the product with the extra price')
    extra_child_line_id = fields.Many2one(comodel_name='sale.order.line',
                                          string='Line extra price', help='',
                                          copy=False)
    total_extra_price = fields.Float(string="Total extra price",
                                     digits=dp.get_precision('Product Price'))
#     invoice_status = fields.Char(string="Invoice Status")

    @api.multi
    def unlink(self):
        for res in self:
            if res.extra_child_line_id:
                res.extra_child_line_id.unlink()
            if res.extra_parent_line_id:
                res.extra_parent_line_id.extra_child_line_id = False
            return super(SaleOrderLine, self).unlink()

    @api.multi
    def update_child(self, line, vals):
        if 'product_uom_qty' in vals and line.extra_child_line_id:
                line.extra_child_line_id.product_uom_qty = \
                    vals['product_uom_qty']

    @api.multi
    def write(self, vals):
        for res in self:
            self.update_child(res, vals)
            return super(SaleOrderLine, self).write(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _get_total_extra(self):
        for order in self:
            for line in order.order_line:
                order.total_extra_price += line.total_extra_price

    total_extra_price = fields.Float(
        string="Total extra price",
        digits=dp.get_precision('Product Price'),
        compute=_get_total_extra)

    @api.one
    def copy(self, default=None):
        res = super(SaleOrder, self).copy(default)
        for line in res.order_line:
            if line.extra_parent_line_id:
                line_in = self.env['sale.order.line'].search(
                    [('extra_child_line_id', '=', line.id),
                     ('order_id', '=', res.id)])
                if not line_in:
                    line.unlink()
        return res

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        result.expand_extra_prices()
        return result

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        self.expand_extra_prices()
        return result

    def prepare_expand_extra_price_vals(self, line, order, sequence, tax_ids):
        dis_policy = line.product_id.discount_policy
        if dis_policy == 'same':
            discount = line.discount
        elif dis_policy == 'only' and line.discount == 100.00:
            discount = 100.00
        else:
            discount = 0
        if line.product_id.extra_price != 0:
            price_unit = line.product_id.extra_price
        else:
            price_unit = line.product_id.product_id_extra.list_price
        vals = {
            'order_id': order.id,
            'name': '-- '+line.product_id.name_extra_price or ' ',
            'sequence': sequence,
            'price_unit': price_unit,
            'tax_id': [(6, 0, tax_ids.ids)],
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_id.uom_id.id,
            'product_packaging': False,
            'discount': discount,
            'qty_to_invoiced': 0,
            'invoice_status': 'no',
            'state': 'draft',
            'extra_parent_line_id': line.id,
            'product_id': line.product_id.product_id_extra.id or None,
        }
        return vals

    @api.multi
    def expand_extra_prices(self):
        updated_orders = []
        order_line_obj = self.env['sale.order.line']
        fiscalp_obj = self.env['account.fiscal.position']
        for order in self:
            fiscal_position = order.fiscal_position_id and fiscalp_obj.browse(
                    order.fiscal_position_id.id) or False
            if not fiscal_position:
                raise Warning('Customer does not have a fiscal position')
            sequence = -1
            reorder = []
            for line in order.order_line:
                sequence += 1
                if sequence > line.sequence:
                    line.sequence = sequence
                else:
                    sequence = line.sequence
                if not line.product_id:
                    continue
                if line.product_id.extra_price == 0:
                    continue
                if line.extra_child_line_id:
                    continue
                sequence += 1
                tax_ids = fiscal_position.map_tax(
                    line.product_id.product_id_extra.taxes_id)
                vals = self.prepare_expand_extra_price_vals(
                    line, order, sequence, tax_ids)

                extra_line = order_line_obj.create(vals)
                if order.id not in updated_orders:
                    updated_orders.append(order.id)
                line.extra_child_line_id = extra_line.id
                line.total_extra_price = extra_line.price_subtotal
                if order.company_id.price_extra_included_sale:
                    extra_line.unlink()
                for line_id in reorder:
                    line_id.sequence = sequence
                    sequence += 1
