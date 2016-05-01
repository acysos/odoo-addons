# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"
    
    def _price_rule_get_multi(self, cr, uid, pricelist,
                              products_by_qty_by_partner, context=None):
        res = super(product_pricelist, self)._price_rule_get_multi(
            cr, uid, pricelist, products_by_qty_by_partner, context)
        for key, value in res.iteritems():
            rule = self.pool.get('product.pricelist.item').browse(
                cr, uid, value[1], context=context)
            if rule.base == -2:
                product = self.pool.get('product.product').browse(cr, uid, key,
                                                                  context)
                qty_uom_id = context.get('uom') or product.uom_id.id
                for prod, qty, partner in products_by_qty_by_partner:
                    if prod == product:
                        continue
                seller = False
                for seller_id in product.seller_ids:
                    if (not partner) or (seller_id.name.id != partner):
                        continue
                    seller = seller_id
                if not seller and product.seller_ids:
                    seller = product.seller_ids[0]
                if seller:
                    qty_in_seller_uom = qty
                    seller_uom = seller.product_uom.id
                    if qty_uom_id != seller_uom:
                        qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                    price_uom_id = seller_uom
                    for line in seller.pricelist_ids:
                        if line.min_quantity <= qty_in_seller_uom:
                            value += (line.discount,)
            else:
                value += (0,)
            res[key] = value
        return res
    
    def disc_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        return dict((key, price[2]) for key, price in self.price_rule_get(cr, uid, ids, prod_id, qty, partner=partner, context=context).items())
    