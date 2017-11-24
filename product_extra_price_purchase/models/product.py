# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Alexander Ezquebo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class pricelist_partnerinfo(models.Model):
    _inherit = 'pricelist.partnerinfo'

    extra_price = fields.Float(
        string='Extra Price', required=True,
        digits=dp.get_precision('Product Price'))


class product_template(models.Model):
    _inherit = "product.template"

    extra_price_purchase = fields.Float(
        'Purchase Extra Price',
        digits=dp.get_precision('Product Price'),
        help="Purchase extra price to show in the invoice like a line")

    @api.onchange('product_id_extra')
    @api.multi
    def onchange_product_id_extra(self):
        for res in self:
            if res.product_id_extra:
                res.extra_price = \
                    res.product_id_extra.product_tmpl_id.list_price
                res.name_extra_price = res.product_id_extra.name
                res.extra_price_purchase = \
                    res.product_id_extra.product_tmpl_id.list_price


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def is_extra_product(self):
        product_obj = self.env['product.product']
        for res in self:
            products = product_obj.search(
                [('product_extra_price', '!=', False)])
            ids = []
            for product in products:
                if product.product_extra_price not in ids:
                    ids.append(product.product_extra_price)
            return ids

    @api.onchange('product_id_extra')
    @api.multi
    def onchange_product_id_extra(self):
        for res in self:
            if res.product_id_extra:
                res.extra_price = \
                    res.product_id_extra.product_tmpl_id.list_price
                res.name_extra_price = res.product_id_extra.name
                res.extra_price_purchase = \
                    res.product_id_extra.product_tmpl_id.list_price
