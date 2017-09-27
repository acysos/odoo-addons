# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

from osv import osv
from osv import fields
import decimal_precision as dp
from tools.translate import _
import time

class pos_order(osv.osv):
    _inherit = 'pos.order'
    
    def create_picking(self, cr, uid, ids, context=None):
        super(pos_order, self).create_picking(cr, uid, ids, context=None)
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        pos_line_obj = self.pool.get('pos.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            if not order.state=='draft':
                continue
            location_id = order.shop_id.warehouse_id.lot_stock_id.id
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            values = {'pos_id':order.id}
            for payment in order.statement_ids:
                if payment.statement_id.journal_id.to_invoiced:
                    values['invoice_state'] = '2binvoiced'
            picking_obj.write(cr,uid,[order.picking_id.id], values)
            for line in order.picking_id.move_lines:
                values = {}
                if line.location_id.id == output_id and line.location_dest_id.id == location_id:
                    values['negative'] = True
                pos_line_id = pos_line_obj.search(cr,uid,
                      [('name','=',line.name)])[0]
                if pos_line_id:
                    values['pos_line_id'] = pos_line_id
                move_obj.write(cr, uid, [line.id], values)
        return True
        
pos_order()