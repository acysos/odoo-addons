# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_extra_price = fields.Many2one(string='Extra price product',
                                          comodel_name='product.product')
    qty_extra_price = fields.Float(string='Extra price qty',
                                   compute='get_extra_price_qty', store = True)
    name_extra_price = fields.Char(string='Extra price name')
    discount_extra_price = fields.Float(string='Extra price discount',
                                        compute='get_extra_discount',
                                        store= True)


    def prepare_extra_price_vals(self, vals, product):
        vals['product_extra_price'] = product.product_id_extra.id
        vals['name_extra_price'] = product.name_extra_price

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        product = self.env['product.product'].search(
            [('id', '=', vals['product_id'])])
        if product.product_id_extra:
            self.prepare_extra_price_vals(vals, product)
        return super(StockMove, self).create(vals)

    @api.depends('product_qty')
    @api.multi
    def get_extra_price_qty(self):
        for res in self:
            if res.product_id.product_id_extra:
                res.qty_extra_price = \
                    res.product_id.extra_price_qty * res.product_qty
            else:
                res.qty_extra_price = 0

    @api.depends('product_extra_price')
    @api.multi
    def get_extra_discount(self):
        for res in self:
            if res.procurement_id.sale_line_id:
                sale_line = res.procurement_id.sale_line_id
                res.discount_extra_price = \
                    sale_line.extra_child_line_id.discount
            else:
                res.discount_extra_price = 0

    @api.multi
    def get_amount_total(self, move):
        untax = move.product_id.extra_price * move.qty_extra_price
        untax = untax - (untax * (move.discount_extra_price/100))
        tax = 0
        for t in move.product_extra_price.taxes_id:
            tax = tax + (untax * t.amount)
        return [tax, untax]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def get_extra_price_qty(self):
        for res in self:
            total = 0
            for move in res.move_ids:
                total = total + move.qty_extra_price
            res.extra_price_qty = total

    @api.multi
    def get_extra_amount_total(self):
        for res in self:
            total = 0
            total_untax = 0
            for move in res.move_lines:
                aux = move.get_amount_total(move)
                total = total + aux[0] + aux[1]
                total_untax = total_untax + aux[1]
            res.extra_price_amount_total = total
            res.extra_price_untax_total = total_untax

    @api.multi
    @api.depends('sale_id.amount_untaxed', 'sale_id.amount_tax',
                 'sale_id.amount_total')
    def _compute_amount(self):
        for res in self:
            if res.sale_id:
                tax_extra = 0
                untax_extra = 0
                for move in res.move_lines:
                    aux = move.get_amount_total(move)
                    tax_extra = tax_extra + aux[0]
                    untax_extra += aux[1]
                if res.pack_operation_ids:
                    for operation in res.pack_operation_ids:
                        res.amount_untaxed += operation.sale_subtotal
                        res.amount_tax += operation.sale_taxes
                    res.amount_total = res.amount_untaxed + res.amount_tax + \
                        tax_extra + untax_extra
                    res.amount_untaxed += untax_extra
                    res.amount_tax += tax_extra
                else:
                    for move in res.move_lines:
                        res.amount_untaxed += move.sale_subtotal
                        res.amount_tax += move.sale_taxes
                    res.amount_total = res.amount_untaxed + res.amount_tax + \
                        tax_extra + untax_extra
                    res.amount_untaxed += untax_extra
                    res.amount_tax += tax_extra


    extra_price_qty = fields.Float(string='extra price quantity',
                                   compute='get_extra_price_qty')
    extra_price_untax_total = fields.Float(string='Extra price untax',
                                           compute='get_extra_amount_total')
    extra_price_amount_total = fields.Float(string='extra price amount total',
                                            compute='get_extra_amount_total')
