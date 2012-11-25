# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
from datetime import datetime
from dateutil.relativedelta import relativedelta

import netsvc
from osv import fields, osv
from tools.translate import _
from decimal import Decimal
import decimal_precision as dp

class pos_order(osv.osv):
    _inherit = "pos.order"
    
    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        property_obj = self.pool.get("ir.property")
        move_obj=self.pool.get('stock.move')
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            if not order.picking_id:
                new = True
                picking_id = picking_obj.create(cr, uid, {
                    'name': pick_name,
                    'origin': order.name,
                    'type': 'out',
                    'state': 'draft',
                    'move_type': 'direct',
                    'note': 'POS notes ' + (order.note or ""),
                    'invoice_state': 'none',
                    'auto_picking': True,
                    'pos_order': order.id,
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            else:
                picking_id = order.picking_id.id
                picking_obj.write(cr, uid, [picking_id], {'auto_picking': True}, context=context)
                picking = picking_obj.browse(cr, uid, [picking_id], context=context)[0]
                new = False

                # split the picking (if product quantity has changed):
                diff_dict = self._get_qty_differences(orders, picking)
                if diff_dict:
                    self._split_picking(cr, uid, ids, context, picking, diff_dict)

            if new:
                for line in order.lines:
                    if line.product_id and line.product_id.type == 'service':
                        continue
                    prop_ids = property_obj.search(cr, uid, [('name', '=', 'property_stock_customer')], context=context)
                    val = property_obj.browse(cr, uid, prop_ids[0], context=context).value_reference
                    cr.execute("SELECT s.id FROM stock_location s, stock_warehouse w WHERE w.lot_stock_id = s.id AND w.id = %s", (order.shop_id.warehouse_id.id, ))
                    res = cr.fetchone()
                    location_id = res and res[0] or None
                    stock_dest_id = val.id
                    if line.qty < 0:
                        location_id, stock_dest_id = stock_dest_id, location_id
                    if line.qty < 0:
                        move_obj.create(cr, uid, {
                                'name': '(POS %d)' % (order.id, ),
                                'product_uom': line.product_id.uom_id.id,
                                'product_uos': line.product_id.uom_id.id,
                                'picking_id': picking_id,
                                'product_id': line.product_id.id,
                                'product_uos_qty': abs(line.qty),
                                'product_qty': abs(line.qty),
                                'tracking_id': False,
                                'pos_line_id': line.id,
                                'state': 'waiting',
                                'location_id': stock_dest_id,
                                'location_dest_id': location_id,
                            }, context=context)
                    else:
                        move_obj.create(cr, uid, {
                                'name': '(POS %d)' % (order.id, ),
                                'product_uom': line.product_id.uom_id.id,
                                'product_uos': line.product_id.uom_id.id,
                                'picking_id': picking_id,
                                'product_id': line.product_id.id,
                                'product_uos_qty': abs(line.qty),
                                'product_qty': abs(line.qty),
                                'tracking_id': False,
                                'pos_line_id': line.id,
                                'state': 'waiting',
                                'location_id': location_id,
                                'location_dest_id': stock_dest_id,
                            }, context=context)

            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            picking_obj.force_assign(cr, uid, [picking_id], context)
        return True
    
pos_order()