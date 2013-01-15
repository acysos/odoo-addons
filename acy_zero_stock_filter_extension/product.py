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

from osv import fields,osv
from tools.translate import _
import decimal_precision as dp

class product_product(osv.osv):
    _inherit = "product.product"
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        return super(product_product,self)._product_available(cr, uid, ids, field_names=field_names, arg=arg, context=context)
    
    def _virtual_available_search(self, cr, uid, obj, name, args, context=None):
        ops = ['>','<=']
        prod_ids = ()
        if not len(args):
            return []
        prod_ids = []
        for a in args:
            operator = a[1]
            value = a[2]
            if not operator in ops:
                raise osv.except_osv(_('Error !'), _('Operator %s not suported in searches for virtual_available (product.product).' % operator))
            if operator == '>':
                todos = self.search(cr, uid, [])
                ids = self.read(cr, uid, todos, ['virtual_available'])
                for d in ids:
                    if d['virtual_available'] > 0:
                        prod_ids.append(d['id'])
            if operator == '<=':
                todos = self.search(cr, uid, [])
                ids = self.read(cr, uid, todos, ['virtual_available'])
                for d in ids:
                    if d['virtual_available'] <= 0:
                        prod_ids.append(d['id'])
        return [('id','in',tuple(prod_ids))]
                    
    _columns = {
        'virtual_available': fields.function(_product_available, fnct_search=_virtual_available_search, method=True, type='float', string='Virtual Stock', help="Future stock for this product according to the selected locations or all internal if none have been selected. Computed as: Real Stock - Outgoing + Incoming.", multi='qty_available', digits_compute=dp.get_precision('Product UoM')),
    }
    
product_product()