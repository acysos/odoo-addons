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

from osv import osv, fields
from tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    
    def update_not_invoiced_sales(self, cr, uid, ids, vals, context=None):
        not_inv_orders = self.pool.get('sale.order').search(cr,uid,[('invoiced_rate','<',100)])
        product = self.pool.get('product.product').browse(cr,uid,ids[0])
        for order in self.pool.get('sale.order').browse(cr,uid,not_inv_orders):
            for line in order.order_line:
                if line.product_id.id == product.id:
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [order.partner_id.property_product_pricelist.id],
                    line.product_id.id, line.product_uom_qty or 1.0, order.partner_id.id, {
                        'uom': line.product_uos.id,
                        'date': order.date_order,
                        })[order.partner_id.property_product_pricelist.id]
                    self.pool.get('sale.order.line').write(cr,uid,[line.id],{'price_unit':price})
                    order.button_dummy()
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_template,self).write(cr, uid, ids, vals, context)
        self.update_not_invoiced_sales(cr, uid, ids, context)
        return res
    
product_template()