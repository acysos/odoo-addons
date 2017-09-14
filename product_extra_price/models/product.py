# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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

