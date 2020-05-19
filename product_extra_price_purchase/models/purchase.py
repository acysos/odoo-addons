# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Alexander Ezquebo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'sequence asc'

    extra_parent_line_id = fields.Many2one(
        comodel_name='purchase.order.line', string='Extra Price',
        help='The line that contain the product with the extra price',
        copy=False)
    extra_child_line_id = fields.Many2one(
        comodel_name='purchase.order.line', string='Line extra price',
        help='', copy=False)
    sequence = fields.Integer(
        string='Sequence', default=10,
        help="Gives the sequence order when displaying a "
        "list of purchase order lines.")
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
            return super(PurchaseOrderLine, self).unlink()

    @api.multi
    def update_child(self, line, vals):
        if 'product_qty' in vals and line.extra_child_line_id:
                line.extra_child_line_id.rpoduct_qty = vals['product_uom_qty']

    @api.multi
    def write(self, vals):
        for res in self:
            self.update_child(res, vals)
            return super(PurchaseOrderLine, self).write(vals)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
        res = super(PurchaseOrder, self).copy(default)
        for line in res.order_line:
            if line.extra_parent_line_id:
                line_in = self.env['purchase.order.line'].search(
                    [('extra_child_line_id', '=', line.id),
                     ('order_id', '=', res.id)])
                if not line_in:
                    line.unlink()
        return res

    @api.model
    def create(self, vals):
        result = super(PurchaseOrder, self).create(vals)
        result.expand_extra_prices()
        return result

    @api.multi
    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        self.expand_extra_prices()
        return result

    def prepare_expand_extra_prices(
            self, line, tax_ids, extra_price, order, sequence):
        dis_policy = line.product_id.discount_policy
        if dis_policy == 'same':
            discount = line.discount
        elif dis_policy == 'only' and line.discount == 100.00:
            discount = 100.00
        else:
            discount = 0
        if line.product_id.name_extra_price:
            extra_price_name = line.product_id.name_extra_price
        else:
            extra_price_name = '*'
        vals = {'name': '-- ' + extra_price_name,
                'product_qty': line.product_qty,
                'date_planned': line.date_planned,
                'taxes_id': [(6, 0, tax_ids.ids)],
                'product_uom': line.product_uom.id,
                'discount': discount,
                'price_unit': extra_price,
                'order_id': order.id,
                'account_analytic_id': line.account_analytic_id.id,
                'state': 'draft',
                'qty_to_invoiced': 0,
                'invoice_status': 'no',
                'sequence': sequence,
                'extra_parent_line_id': line.id,
                'product_id': line.product_id.product_id_extra.id or None,
                }
        return vals

    @api.multi
    def expand_extra_prices(self):
        updated_orders = []
        order_line_obj = self.env['purchase.order.line']
        fiscalp_obj = self.env['account.fiscal.position']
        for order in self:
            fiscal_position = order.fiscal_position_id and fiscalp_obj.browse(
                    order.fiscal_position_id.id) or False
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
                if line.extra_child_line_id:
                    continue
                if line.product_id.extra_price_purchase != 0:
                    extra_price = line.product_id.extra_price_purchase
                else:
                    extra_price = \
                        line.product_id.product_id_extra.standard_price
                if extra_price == 0:
                    continue
                sequence += 1
                tax_ids = fiscal_position.map_tax(
                    line.product_id.product_id_extra.taxes_id)
                vals = self.prepare_expand_extra_prices(
                    line, tax_ids, extra_price, order, sequence)

                extra_line = order_line_obj.create(vals)
                if not order.id in updated_orders:
                    updated_orders.append( order.id )
                line.extra_child_line_id = extra_line.id
                line.total_extra_price = extra_line.price_subtotal
                if order.company_id.price_extra_included_purchase:
                    extra_line.unlink()
                for line_id in reorder:
                    line_id.sequence = sequence
                    sequence += 1
