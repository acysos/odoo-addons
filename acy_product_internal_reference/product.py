# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import decimal_precision as dp

import math
import re
from tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'internal_reference': fields.char('Internal Reference', size=64),
        'internal_name': fields.char('Internal Name', size=128, required=True, translate=True, select=True),
    }
    
product_template()

class product_product(osv.osv):
    _inherit = "product.product"
    
    def _get_partner_code_name(self, cr, uid, ids, product, partner_id, context=None):
        for supinfo in product.seller_ids:
            if supinfo.name.id == partner_id:
                return {'code': supinfo.product_code or product.default_code, 'name': supinfo.product_name or product.name, 'variants': ''}
        res = {'code': product.default_code, 'name': product.name, 'variants': product.variants,'internal_reference':product.internal_reference}
        return res
        
    def _product_code(self, cr, uid, ids, name, arg, context=None):
        print 'code'
        res = {}
        if context is None:
            context = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = self._get_partner_code_name(cr, uid, [], p, context.get('partner_id', None), context=context)['code']
        return res
    
    def _product_internal_ref(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for p in self.browse(cr, uid, ids, context=context):
            data = self._get_partner_code_name(cr, uid, [], p, context.get('partner_id', None), context=context)
            if not data['variants']:
                data['variants'] = p.variants
            if not data['code']:
                data['code'] = p.code
            if not data['name']:
                data['name'] = p.name
            res[p.id]=''
            if (data['code'] or data['internal_reference']): res[p.id] += '['
            res[p.id] += (data['code'] or '')+(data['internal_reference'] and ('-'+data['internal_reference']) or '')
            if (data['code'] or data['internal_reference']): res[p.id] += '] '
            res[p.id] += (data['name'] or '') + (data['variants'] and (' - '+data['variants']) or '')
        return res
            
    _columns = {
        'internal_ref' : fields.function(_product_internal_ref, method=True, type='char', string='Internal ref'),
    }
    
    _order = 'default_code,name_template'
            
product_product()