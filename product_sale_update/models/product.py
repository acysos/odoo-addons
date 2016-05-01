# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    
    def update_not_invoiced_sales(self, cr, uid, ids, vals, context=None):
        prod_tmpl = self.pool.get('product.template').browse(cr,uid,ids[0])
        for product in prod_tmpl.product_variant_ids:
            not_inv_lines = self.pool.get('sale.order.line').search(cr, uid, [('product_id','=',product.id),('invoiced','=',False)])
            for line in self.pool.get('sale.order.line').browse(cr, uid, not_inv_lines):
                price = self.pool.get('product.pricelist').price_get(cr, uid, [line.order_id.partner_id.property_product_pricelist.id],
                            line.product_id.id, line.product_uom_qty or 1.0, line.order_id.partner_id.id, {
                                'uom': line.product_uos.id,
                                'date': line.order_id.date_order,
                                })[line.order_id.partner_id.property_product_pricelist.id]
                self.pool.get('sale.order.line').write(cr,uid,[line.id],{'price_unit':price})
                line.order_id.button_dummy()
            
        return not_inv_lines
    
#     def update_not_invoiced_sales(self, cr, uid, ids, vals, context=None):
#         not_inv_orders = self.pool.get('sale.order').search(cr,uid,[('invoiced_rate','<',100.0)])
#         print "Not invoiced sales"
#         print len(not_inv_orders)
#         product = self.pool.get('product.product').browse(cr,uid,ids[0])
#         for order in self.pool.get('sale.order').browse(cr,uid,not_inv_orders):
#             if order.invoiced_rate < 100.0:
#                 for line in order.order_line:
#                     if line.product_id.id == product.id:
#                         price = self.pool.get('product.pricelist').price_get(cr, uid, [order.partner_id.property_product_pricelist.id],
#                         line.product_id.id, line.product_uom_qty or 1.0, order.partner_id.id, {
#                             'uom': line.product_uos.id,
#                             'date': order.date_order,
#                             })[order.partner_id.property_product_pricelist.id]
#                         self.pool.get('sale.order.line').write(cr,uid,[line.id],{'price_unit':price})
#                         order.button_dummy()
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_template,self).write(cr, uid, ids, vals, context)
        self.update_not_invoiced_sales(cr, uid, ids, context)
        return res
