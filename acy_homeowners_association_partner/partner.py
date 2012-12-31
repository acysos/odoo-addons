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
from tools.translate import _
import tools
import os

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _categories_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for partner in self.browse(cr,uid,ids,context):
            categories = ''
            for category in partner.category_id:
              categories += category.name
              if len(partner.category_id) > 1:
                categories += ' / '
            res[partner.id] = categories
        return res
              
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
                if not ids:
                    ids = self.search(cr, uid, [('floor', operator, name)] + args, limit=limit, context=context)
                    if not ids:
                        ids = self.search(cr, uid, [('parking', operator, name)] + args, limit=limit, context=context)
                        if not ids:
                            ids = self.search(cr, uid, [('boxroom', operator, name)] + args, limit=limit,context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
    
    _columns = {
        'floor': fields.char('Floor', size=128, select=True),
        'stairs': fields.selection([('L','Left'),('C', 'Center'),('R', 'Right')], 'Stairs', required=False),
	    'parking': fields.char('Parking', size=128, select=True),
        'boxroom': fields.char('Boxroom', size=128, select=True),
		'percentage_home': fields.float('Percentage Home',digits=(2,4)),
		'percentage_parking': fields.float('Percentage Parking',digits=(2,4)),
        'percentage_premises': fields.float('Percentage Premises',digits=(2,4)),
        'percentage_boxroom': fields.float('Percentage Boxroom',digits=(2,4)),
        'other_percentage': fields.float('Other Percentage',digits=(2,4)),
        'categories': fields.function(_categories_get, method=True, type='char', size=128, string='Categories', readonly=True),
        'insurance_number': fields.char('Insurance Number', size=128, select=True),
        'resident': fields.boolean('No Resident'),
    }
    
    _defaults = {
        'resident': lambda *a: 'Y',
    }
res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
