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
import decimal_precision as dp

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def _shipped_rate_finish(self, cr, uid, ids, name, arg, context=None):
        res = super(purchase_order, self)._shipped_rate(cr, uid,
            ids, name, arg, context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.shipped:
                res[order.id] = 100.0
        return res
    
    _columns = {
        'shipped_rate': fields.function(_shipped_rate_finish, method=True, string='Received', type='float'),
    }
                
    def cancel_shipped(self, cr, uid, ids, context):
        pick_obj = self.pool.get('stock.picking')
        for id in ids:
            pick_ids = pick_obj.search(cr,uid,[('purchase_id','=',id)])
            picks = pick_obj.browse(cr,uid,pick_ids,context)
            for pick in picks:
                if pick.state == 'assigned':
                    pick_obj.action_cancel(cr,uid,[pick.id])
            self.write(cr,uid,id,{'state':'done','shipped':True},context)
        return True
    
purchase_order()