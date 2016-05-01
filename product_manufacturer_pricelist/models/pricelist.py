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

import time
from openerp import models, fields, osv
from openerp import tools
from openerp.tools.translate import _
from openerp.exceptions import except_orm


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    manufacturer = fields.Many2one('res.partner', 'Manufacturer')

    
class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'
    
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}
        
        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise except_orm(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))
        
        manufacturer_ids = {}
        categ_ids = {}
        for p in products:
            if p.manufacturer:
                manufacturer = p.manufacturer
                manufacturer_ids[manufacturer.id] = True
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        if len(manufacturer_ids) > 0:
            manufacturer_ids = manufacturer_ids.keys()
            categ_ids = categ_ids.keys()
    
            is_product_template = products[0]._name == "product.template"
            if is_product_template:
                prod_tmpl_ids = [tmpl.id for tmpl in products]
                prod_ids = [product.id for product in tmpl.product_variant_ids for tmpl in products]
            else:
                prod_ids = [product.id for product in products]
                prod_tmpl_ids = [product.product_tmpl_id.id for product in products]
            
            # Load all rules
            cr.execute(
                'SELECT i.id '
                'FROM product_pricelist_item AS i '
                'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
                    'AND (product_id IS NULL OR (product_id = any(%s))) '
                    'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
                    'AND ((manufacturer IS NULL) OR (manufacturer = any(%s))) '
                    'AND (price_version_id = %s) '
                'ORDER BY sequence, min_quantity desc',
                (prod_tmpl_ids, prod_ids, categ_ids, manufacturer_ids, version.id))
            
            item_ids = [x[0] for x in cr.fetchall()]
            items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)
            
            price_types = {}
    
            results = {}
            for product, qty, partner in products_by_qty_by_partner:
                uom_price_already_computed = False
                results[product.id] = 0.0
                price = False
                rule_id = False
                for rule in items:
                    if rule.manufacturer and product.manufacturer.id != rule.manufacturer.id:
                        continue
                    if 'uom' in context and product.uom_id and context['uom'] != product.uom_id.id:
                        try:
                            qty_in_product_uom = product_uom_obj._compute_qty(cr, uid, context['uom'], qty, product.uom_id.id, dict(context.items() + [('raise-exception', False)]))
                        except except_orm:
                            qty_in_product_uom = qty
                    else:
                        qty_in_product_uom = qty
                    if rule.min_quantity and qty_in_product_uom<rule.min_quantity:
                        continue
                    if is_product_template:
                        if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                            continue
                        if rule.product_id:
                            continue
                    else:
                        if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                            continue
                        if rule.product_id and product.id != rule.product_id.id:
                            continue
    
                    if rule.categ_id:
                        cat = product.categ_id
                        while cat:
                            if cat.id == rule.categ_id.id:
                                break
                            cat = cat.parent_id
                        if not cat:
                            continue
                    if rule.base == -1:
                        if rule.base_pricelist_id:
                            price_tmp = self._price_get_multi(cr, uid,
                                    rule.base_pricelist_id, [(product,
                                    qty, False)], context=context)[product.id]
                            ptype_src = rule.base_pricelist_id.currency_id.id
                            uom_price_already_computed = True
                            price = currency_obj.compute(cr, uid,
                                    ptype_src, pricelist.currency_id.id,
                                    price_tmp, round=False,
                                    context=context)
                    elif rule.base == -2:
                        seller = False
                        for seller_id in product.seller_ids:
                            if (not partner) or (seller_id.name.id != partner):
                                continue
                            seller = seller_id
                        if not seller and product.seller_ids:
                            seller = product.seller_ids[0]
                        if seller:
                            qty_in_seller_uom = qty
                            from_uom = context.get('uom') or product.uom_id.id
                            seller_uom = seller.product_uom and seller.product_uom.id or False
                            if seller_uom and from_uom and from_uom != seller_uom:
                                qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, from_uom, qty, to_uom_id=seller_uom)
                            else:
                                uom_price_already_computed = True
                            for line in seller.pricelist_ids:
                                if line.min_quantity <= qty_in_seller_uom:
                                    price = line.price
    
                    else:
                        if rule.base not in price_types:
                            price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                        price_type = price_types[rule.base]
    
                        uom_price_already_computed = True
                        price = currency_obj.compute(cr, uid,
                                price_type.currency_id.id, pricelist.currency_id.id,
                                product_obj._price_get(cr, uid, [product],
                                price_type.field, context=context)[product.id], round=False, context=context)
                    if price is not False:
                        price_limit = price
                        price = price * (1.0+(rule.price_discount or 0.0))
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)
                        if context.get('uom'):
                            # compute price_surcharge based on reference uom
                            factor = product_uom_obj.browse(cr, uid, context.get('uom'), context=context).factor
                        else:
                            factor = 1.0
                        price += (rule.price_surcharge or 0.0) / factor
                        if rule.price_min_margin:
                            price = max(price, price_limit+rule.price_min_margin)
                        if rule.price_max_margin:
                            price = min(price, price_limit+rule.price_max_margin)
                        rule_id = rule.id
                    break
    
                if price:
                    if 'uom' in context and not uom_price_already_computed:
                        uom = product.uos_id or product.uom_id
                        price = product_uom_obj._compute_price(cr, uid, uom.id, price, context['uom'])
    
                results[product.id] = (price, rule_id)
        else:
            results = {}
        if len(results) == 0:
            results = super(ProductPriceList, self)._price_rule_get_multi(cr, uid, pricelist, products_by_qty_by_partner, context=None)
        
        return results
