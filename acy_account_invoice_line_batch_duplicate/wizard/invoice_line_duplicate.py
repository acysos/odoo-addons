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

class invoice_line_duplicate(osv.osv_memory):
    _name = 'wizard.invoice.duplicate.line'
 
    _columns = {
        'description': fields.char('Description', size=64, help='Leave blank, to copy the description of the original line'),
        'price': fields.float('Price', digits_compute=dp.get_precision('Account'), help='Leave blank, to copy the original price'),
    }
 
    def copy_invoice_line(self, cr, uid, ids, context):
        if context is None:
            context = {}
        form_obj = self.browse(cr, uid, ids)[0]
        line_obj = self.pool.get('account.invoice.line')
        lines = line_obj.browse(cr,uid,context['active_ids'],context)

        for line in lines:
            if line.invoice_id.state == 'draft':
                if form_obj.description:
                    description = form_obj.description
                else:
                    description = line.name
                if form_obj.price != 0:
                    price = form_obj.price
                else:
                    price = line.price_unit
                line_obj.copy(cr,uid,line.id,{'name':description,'price_unit':price}, context)
            else:
                raise osv.except_osv(_('UserError'),
                    _('You only can duplicate a line in a draft invoice'))
 
        return {'type': 'ir.actions.act_window_close'}

invoice_line_duplicate()