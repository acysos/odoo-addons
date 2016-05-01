# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.one
    def _compute_total_standard_price(self):
        for line in self.bom_line_ids:
            self.total_standard_price += line.supplier_price_discount * line.product_qty
            self.total_standard_price += line.childs_standard_price * line.product_qty


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    @api.one
    def _compute_childs_standard_price(self):
        if self.product_id.seller_ids:
            self.childs_standard_price = 0
            for line in self.child_line_ids:
                self.childs_standard_price += (line.supplier_price_discount +
                                               line.childs_standard_price) * line.product_qty
        else:
            super(MrpBomLine, self)._compute_childs_standard_price()

    @api.one
    def _compute_discount(self):
        if self.product_id.seller_ids:
            if self.product_id.seller_ids[0].pricelist_ids:
                plist = self.product_id.seller_ids[0].pricelist_ids[0]
                self.supplier_discount = plist.discount
            else:
                self.supplier_discount = 0
        else:
            self.supplier_discount = 0

    @api.one
    def _compute_price_discount(self):
        if self.product_id.seller_ids:
            if self.product_id.seller_ids[0].pricelist_ids:
                plist = self.product_id.seller_ids[0].pricelist_ids[0]
                self.supplier_price_discount = plist.price_with_disc
            else:
                self.supplier_price_discount = self.product_id.standard_price
        else:
            self.supplier_price_discount = self.product_id.standard_price

    supplier_discount = fields.Float(
        string='Supplier discount', compute='_compute_discount',
        digits_compute=dp.get_precision('Discount'))
    supplier_price_discount = fields.Float(
        string='Price with discount', compute='_compute_price_discount',
        digits_compute=dp.get_precision('Product Price'))
