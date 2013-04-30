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

class product_change_price(osv.osv_memory):
    _name = 'wizard.product.change.price'
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, help="Product to change the price"),
        'description': fields.char('Description', size=256, select=True),
        'percentage': fields.float('Percentage', digits=(16,2)),
        'fixed': fields.float('Fixed', digits=(16,2)),
    }
    
    def change_price(self, cr, uid, ids, context):
        if context is None:
            context = {}
        form_obj = self.browse(cr, uid, ids)[0]
        line_obj = self.pool.get('account.invoice.line')
        inv_obj = self.pool.get('account.invoice')
        invoices = inv_obj.browse(cr,uid,context['active_ids'],context)
        
        for invoice in invoices:
            if invoice.state == 'draft':
                for line in invoice.invoice_line:
                    if line.product_id.id == form_obj.product_id.id:
                        new_price = line.price_unit*(1 + form_obj.percentage) + form_obj.fixed
                        line_obj.write(cr,uid,line.id,{'price_unit':new_price,'name':form_obj.description},context)
            else:
                raise osv.except_osv(_('UserError'),
                    _('You only change the price in a draft invoice'))
                    
        return {'type': 'ir.actions.act_window_close'}
    
product_change_price()