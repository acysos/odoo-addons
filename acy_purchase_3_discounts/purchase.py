# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (c) 2011  NaN Projectes de Programari Lliure S.L.
#                   (http://www.nan-tic.com) All Rights R
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

from datetime import datetime
from osv import osv, fields
from tools.translate import _
import netsvc
import time
import tools

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def action_cancel_draft(self, cr, uid, ids, *args):
        res = super(purchase_order, self).action_cancel_draft(cr, uid,
            ids, *args)
        line_obj = self.pool.get('purchase.order.line')
        for order in self.browse(cr,uid,ids):
            for line in order.order_line:
                line_obj.write(cr,uid,[line.id],{'state':'draft'})
        return True
            
    def inv_line_create(self, cr, uid, a, ol):
        result = super(purchase_order, self).inv_line_create(cr, uid, a, ol)
        result[2]['discount1'] = ol.discount1 or 0.0
        result[2]['discount2'] = ol.discount2 or 0.0
        result[2]['discount3'] = ol.discount3 or 0.0
        return result
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'discount1': fields.float('Discount 1', digits=(10,2)),
        'discount2': fields.float('Discount 2', digits=(10,2)),
        'discount3': fields.float('Discount 3', digits=(10,2)),
        'discount': fields.float( 'Calculated discount', digits=(10,2) , readonly="True" ),
    }
    def _get_discount(self, cr, uid, ids, field_name, field_value, context):
        result = {}
        for line in self.browse(cr,uid,ids,context=context):
            value = 100*(1 - ( (100-line.discount1)/100 *(100-line.discount2)/100 * (100-line.discount3)/100 ))
            result[line.id] = value
        return result
    def onchange_discount(self, cr, uid, ids, discount1,discount2,discount3 ,context=None ):
        if context is None:
            context={}
        result = {'value':{}}
        result['value']['discount']= 100*( 1 - ((100-discount1)/100 * (100-discount2)/100 * (100 - discount3)/100 ) )
        return result
        
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        
        for line in self.browse(cr,uid,ids,context=context):
            value = 100*(1 - ( (100-vals.get('discount1',line.discount1) )/100 *(100-vals.get('discount2',line.discount2))/100 * (100-vals.get('discount3',line.discount3))/100 ))
            vals['discount'] = value
            if not super( purchase_order_line , self ).write( cr, uid,[line.id], vals, context=context ):
                return False

        return True
        
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context ={}
        
        vals['discount'] = 100*( 1 - ((100-vals.get('discount1',0))/100 * (100-vals.get('discount2',0))/100 * (100 - vals.get('discount3',0))/100 ) )
        return super( purchase_order_line, self).create( cr, uid, vals,context )

    def _get_sale_order_state(self, cr, uid, ids, context=None):
        result = {}
        for order in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            for line in order.order_line:
                result[line.id] = True
        return result.keys()
            
    def action_confirm(self, cr, uid, ids, context=None):
        res = super(purchase_order_line, self).action_confirm(cr, uid,
            ids, context)
        prod_obj = self.pool.get('product.product')
        for line in self.browse(cr,uid,ids,context):
            if line.product_id.cost_method == 'standard':
                cost = line.price_subtotal/line.product_qty
                prod_obj.write(cr,uid,line.product_id.id,{'standard_price':cost},context)
        return True
    
purchase_order_line()

class stock_picking( osv.osv ):
    _inherit =  'stock.picking'
        
    def _get_discount_invoice(self, cursor, user, move_line):
        #if move_line.sale_line_id:
            #return move_line.sale_line_id.discount
        if move_line.purchase_line_id:
            line = move_line.purchase_line_id
            return 100*(1 - ( (100-line.discount1)/100 *(100-line.discount2)/100 * (100-line.discount3)/100 ))
        return super(stock_picking, self)._get_discount_invoice(cursor, user, move_line)
    
    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        if move_line.sale_line_id:
            self.pool.get('account.invoice.line').write( cr, uid, [invoice_line_id], {        
                'discount1':move_line.sale_line_id.discount,
                } )
        if move_line.purchase_line_id:
            self.pool.get('account.invoice.line').write( cr, uid, [invoice_line_id], {        
                'discount':move_line.purchase_line_id.discount,
                'discount1':move_line.purchase_line_id.discount1, 
                'discount2':move_line.purchase_line_id.discount2,
                'discount3':move_line.purchase_line_id.discount3,
                } )
        return super( stock_picking, self)._invoice_line_hook( cr, uid, move_line,invoice_line_id )
    
stock_picking()

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    
    _columns = {
        'discount': fields.float( 'Calculated discount', digits=(10,2) , readonly="True" ),
        'discount1': fields.float('Discount 1', digits=(10,2)),
        'discount2': fields.float('Discount 2', digits=(10,2)),
        'discount3': fields.float('Discount 3', digits=(10,2)),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        
        for line in self.browse(cr,uid,ids,context=context):
            discount1 = vals.get('discount1', line.discount1) or 0.0
            discount2 = vals.get('discount2', line.discount2) or 0.0
            discount3 = vals.get('discount3', line.discount3) or 0.0
            value = 100*(1 - ( (100-discount1)/100 *(100-discount2)/100 * (100-discount3)/100 ))
            vals['discount'] = value
            if not super( account_invoice_line , self ).write( cr, uid,[line.id], vals, context=context ):
                return False

        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context ={}
        
        vals['discount'] = 100*( 1 - ((100-vals.get('discount1',0))/100 * (100-vals.get('discount2',0))/100 * (100 - vals.get('discount3',0))/100 ) )
        return super( account_invoice_line, self).create( cr, uid, vals,context )
        
    def _get_discount(self, cr, uid, ids, field_name, field_value, context):
        result = {}
        for line in self.browse(cr,uid,ids,context=context):
            value = 100*(1 - ( (100-line.discount1)/100 *(100-line.discount2)/100 * (100-line.discount3)/100 ))
            result[line.id] = value
        return result


    def onchange_discount(self, cr, uid, ids, discount1,discount2,discount3 ,context=None ):
        if context is None:
            context={}
        result = {'value':{}}
        result['value']['discount']= 100*( 1 - ((100-discount1)/100 * (100-discount2)/100 * (100 - discount3)/100 ) )
        return result
    
account_invoice_line()