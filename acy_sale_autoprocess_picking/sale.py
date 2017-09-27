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
from osv import osv
from osv import fields
import decimal_precision as dp
from tools.translate import _
import time
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _create_pickings_and_procurements(self, cr, uid, order, 
          order_lines, picking_id=False, context=None):
        res = super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, 
            order_lines, picking_id=False, context=None)
        picking_obj = self.pool.get('stock.picking')
        
        picking_id = picking_obj.search(cr,uid,[('sale_id', '=', order.id)], context)[0]
        picking = picking_obj.browse(cr,uid,picking_id,context)
        partial_data = {
            'delivery_date' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        }
        for move in picking.move_lines:
            partial_data['move%s' % (move.id)] = {
                    'product_id': move.product_id.id,
                    'product_qty': move.product_qty,
                    'product_uom': move.product_uom.id,
                    'prodlot_id': move.prodlot_id.id,
            }
        picking_obj.do_partial(cr, uid, [picking.id], partial_data, context=context)
        
        return True

sale_order()

