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
from tools.translate import _

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    _columns = {
        'sale_order_line_seq': fields.char('Sale Order Line Seq', size=64, readonly=False, required=True),
    }
    
    _defaults = {
        'sale_order_line_seq':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'sale.order.line.sequence'),
    }

    def onchange_name(self,cr,uid,ids,sale_order_line_seq,context={}):
        self.pool.get('sale.order.line.seq').create(cr,uid,{'name':sale_order_line_seq,'sequence_line':1})
        return {}
    
    def create(self, cr, uid, vals, context=None):
        result = super(sale_order,self).create(cr, uid, vals, context)
        self.order_lines(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(sale_order,self).write(cr, uid, ids, vals, context)
        self.order_lines(cr, uid, ids, context)
        return result
    
    def order_lines(self, cr, uid, ids, context={}):
        seq_line_obj = self.pool.get('sale.order.line.seq')
        if type(ids) in [int, long]:
            ids = [ids]
        updated_orders = []
        for order in self.browse(cr, uid, ids, context):
            sequence = 0
            reorder = []
            for line in order.order_line:
                sequence += 1
                self.pool.get('sale.order.line').write(cr, uid, [line.id], {
                        'sequence': sequence,
                        }, context)
        seq_line_id = seq_line_obj.search(cr,uid,[('name', '=', order.sale_order_line_seq)],limit=1)[0]
        seq_line = seq_line_obj.browse(cr,uid,seq_line_id)
        seq_line_obj.write(cr,uid,seq_line_id,{'sequence_line':sequence+1})
        return
    
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    _defaults = {
        'sequence' :  0,
    }
    
    def onchange_sequence(self,cr,uid,ids,sale_order_line_seq,sequence,sale_id,context={}):
        seq_line_obj = self.pool.get('sale.order.line.seq')
        sale_obj = self.pool.get('sale.order')
        if sale_order_line_seq:
            seq_line_id = seq_line_obj.search(cr,uid,[('name', '=', sale_order_line_seq)],limit=1)[0]
            seq_line = seq_line_obj.browse(cr,uid,seq_line_id)
            if sequence == 0:
                seq_line_obj.write(cr,uid,seq_line_id,{'sequence_line':seq_line.sequence_line+1})
                return {'value': {'sequence': seq_line.sequence_line}}
            else:
                if not sale_id:
                    raise osv.except_osv(_('Invalid action !'), _('You have to save the sale order before change the sequence line !'))
                else:
                    if seq_line.sequence_line < sequence:
                        seq_line_obj.write(cr,uid,seq_line_id,{'sequence_line':sequence+1})
                    return {'value': {'sequence': sequence}}
        else:
            return
    
sale_order_line()

class sale_order_line_seq(osv.osv):
    _name = 'sale.order.line.seq'
    
    _columns = {
        'name': fields.char('Order Reference', size=64, required=True,
            readonly=True, states={'draft': [('readonly', False)]}, select=True),
        'sequence_line': fields.integer('Sequence'),
    }
        
sale_order_line_seq()