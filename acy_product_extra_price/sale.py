# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'extra_parent_line_id': fields.many2one('sale.order.line', 'Extra Price', help='The line that contain the product with the extra price'),
        'extra_child_line_id': fields.many2one('sale.order.line', 'Line extra price', help=''),
    }
sale_order_line()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def create(self, cr, uid, vals, context=None):
        result = super(sale_order,self).create(cr, uid, vals, context)
        self.expand_extra_prices(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(sale_order,self).write(cr, uid, ids, vals, context)
        self.expand_extra_prices(cr, uid, ids, context)
        return result
    
    def expand_extra_prices(self, cr, uid, ids, context={}):
        if type(ids) in [int, long]:
            ids = [ids]
        updated_orders = []
        for order in self.browse(cr, uid, ids, context):
            fiscal_position = order.fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, order.fiscal_position.id, context) or False
            
            sequence = -1
            reorder = []
            
            for line in order.order_line:
                sequence += 1
            
                if sequence > line.sequence:
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {
                        'sequence': sequence,
                    }, context)
                else:
                    sequence = line.sequence

                if line.state != 'draft':
                    continue
                if not line.product_id:
                    continue
                if line.product_id.extra_price == 0:
                    continue
                if line.extra_child_line_id:
                    continue
                
                sequence += 1
                tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, line.product_id.taxes_id)
                vals = {
                    'order_id': order.id,
                    'name': '--> '+line.product_id.name_extra_price or ' ',
                    'sequence': sequence,
                    'delay': line.product_id.sale_delay or 0.0,
                    'procurement_id': line.procurement_id and line.procurement_id.id or False,
                    'price_unit': line.product_id.extra_price,
                    'tax_id': [(6,0,tax_ids)],
                    'type': line.product_id.procure_method,
                    'property_ids': [(6,0,[])],
                    'address_allotment_id': False,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos_qty': line.product_uos_qty,
                    'product_uos': line.product_uos,
                    'product_packaging': False,
                    'move_ids': [(6,0,[])],
                    'discount': line.discount,
                    'number_packages': False,
                    'notes': False,
                    'th_weight': False,
                    'state': 'draft',
                    'extra_parent_line_id': line.id,
                }
                
                extra_line = self.pool.get('sale.order.line').create(cr, uid, vals, context)
                if not order.id in updated_orders:
                    updated_orders.append( order.id )

                self.pool.get('sale.order.line').write(cr,uid,[line.id],{'extra_child_line_id':extra_line})

                for id in reorder:
                    sequence += 1
                    self.pool.get('sale.order.line').write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)
                
        return
    
sale_order()