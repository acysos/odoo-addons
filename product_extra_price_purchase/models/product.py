# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2017 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
