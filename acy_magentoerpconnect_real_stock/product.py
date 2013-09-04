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

from osv import fields, osv
from tools.translate import _
import netsvc

class product_product(osv.osv):
    _inherit = "product.product"
    
    def export_inventory(self, cr, uid, ids, shop, context):
        logger = netsvc.Logger()
        stock_id = self.pool.get('sale.shop').browse(cr, uid, context['shop_id']).warehouse_id.lot_stock_id.id
        for product in self.browse(cr, uid, ids):
            if product.magento_sku and product.type != 'service':
                qty_available = self.read(cr, uid, product.id, ['qty_available'], {'location': stock_id})['qty_available']
        # Changing Stock Availability to "Out of Stock" in Magento
                # if a product has qty lt or equal to 0.
                is_in_stock = int(qty_available > 0)
                context['conn_obj'].call('product_stock.update', [product.magento_sku, {'qty': qty_available, 'is_in_stock': is_in_stock}])
                logger.notifyChannel('ext synchro', netsvc.LOG_INFO, "Successfully updated stock level at %s for product with SKU %s " %(qty_available, product.magento_sku))
        return True
    
product_product()