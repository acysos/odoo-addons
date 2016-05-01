# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import openerp.addons.decimal_precision as dp

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.seconds != 0:
                qty = line.product_uom_qty * line.seconds
            else:
                qty = line.product_uom_qty
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    def _total_seconds_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.seconds != 0:
                res[line.id] = line.product_uom_qty * line.seconds
        return res
    
    def _seconds_consumed(self, cr, uid, ids, field_name, arg,
                                context=None):
        res = {}
        if context is None:
            context = {}
        seconds = 0
        for line in self.browse(cr, uid, ids, context=context):
            for time in line.time_line_ids:
                seconds += time.seconds
            res[line.id] = seconds
        return res
    
    _columns = {
            'seconds': fields.integer('Seconds'),
            'time_line_ids':fields.one2many('product.time.line',
                                            'sale_order_line_id',
                                            'Programming'),
            'price_subtotal': fields.function(
                  _amount_line, string='Subtotal',
                  digits_compute= dp.get_precision('Account')
                  ),
            'total_seconds_line': fields.function(
                  _total_seconds_line, string='Total Seconds'
                  ), 
            'seconds_consumed': fields.function(
                  _seconds_consumed, string='Seconds Consumed'
                  ), 
    }
    

