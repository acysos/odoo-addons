# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

DISCOUNT_POL = [('same', 'Same as product'), ('only', 'Only 100%'),
                ('independent', 'Independect')]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    extra_price = fields.Float(
        string='Extra Price',
        digits=dp.get_precision('Product Price'),
        help="Extra price to show in the invoice like a line")
    name_extra_price = fields.Char(
        string='Description Extra Price', size=64,
        help="This description is used for the description of the line",
        translate=True)
    product_id_extra = fields.Many2one(string='Product for extra price',
                                       comodel_name='product.product')
    discount_policy = fields.Selection(
        string='Discount policy',
        selection=DISCOUNT_POL, default='independent')

    @api.onchange('product_id_extra')
    @api.multi
    def onchange_product_id_extra(self):
        for res in self:
            if res.product_id_extra:
                res.extra_price = \
                    res.product_id_extra.product_tmpl_id.list_price
                res.name_extra_price = res.product_id_extra.name


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('product_id_extra')
    @api.multi
    def onchange_product_id_extra(self):
        for res in self:
            if res.product_id_extra:
                res.extra_price = \
                    res.product_id_extra.product_tmpl_id.list_price
                res.name_extra_price = res.product_id_extra.name
