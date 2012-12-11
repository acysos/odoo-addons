##############################################################################
#
# Copyright (c) 2010 Javier Duran <javieredm@gmail.com> All Rights Reserved.
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Updated to OpenERP 6.0
#                       Ignacio Ibeas <ignacio@acysos.com
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields
from osv import osv


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        ids=[]
        if not args:
            args=[]
        if not context:
            context={}
        if context and context.has_key('partner_id') and context['partner_id']:
            cr.execute('SELECT p.id ' \
                    'FROM product_product AS p ' \
                    'INNER JOIN product_template AS t ' \
                    'ON p.product_tmpl_id=t.id ' \
                    'INNER JOIN product_supplierinfo AS ps ' \
                    'ON ps.product_id=p.id ' \
                    'WHERE ps.name = '+str(context['partner_id'])+' ' \
                    'AND p.default_code = \''+str(name)+'\' ' \
                    'AND t.purchase_ok = True ' \
                    'ORDER BY p.id')
            res = cr.fetchall()
            ids = map(lambda x:x[0], res)
            if not len(ids):
                cr.execute('SELECT p.id ' \
                    'FROM product_product AS p ' \
                    'INNER JOIN product_template AS t ' \
                    'ON p.product_tmpl_id=t.id ' \
                    'INNER JOIN product_supplierinfo AS ps ' \
                    'ON ps.product_id=p.id ' \
                    'WHERE ps.name = '+str(context['partner_id'])+' ' \
                    'AND p.ean13 = \''+str(name)+'\' ' \
                    'AND t.purchase_ok = True ' \
                    'ORDER BY p.id')
                res = cr.fetchall()
                ids = map(lambda x:x[0], res)
            if not len(ids):
                if operator in ('like', 'ilike'):
                    name='%'+name+'%'
                cr.execute('SELECT p.id ' \
                    'FROM product_product AS p ' \
                    'INNER JOIN product_template AS t ' \
                    'ON p.product_tmpl_id=t.id ' \
                    'INNER JOIN product_supplierinfo AS ps ' \
                    'ON ps.product_id=p.id ' \
                    'WHERE ps.name = '+str(context['partner_id'])+' ' \
                    'AND p.default_code '+operator+'   \''+str(name)+'\' ' \
                    'AND t.purchase_ok = True ' \
                    'ORDER BY p.id')
                res = cr.fetchall()
                ids = map(lambda x:x[0], res)
                cr.execute('SELECT p.id ' \
                    'FROM product_product AS p ' \
                    'INNER JOIN product_template AS t ' \
                    'ON p.product_tmpl_id=t.id ' \
                    'INNER JOIN product_supplierinfo AS ps ' \
                    'ON ps.product_id=p.id ' \
                    'WHERE ps.name = '+str(context['partner_id'])+' ' \
                    'AND t.name '+operator+'   \''+str(name)+'\' ' \
                    'AND t.purchase_ok = True ' \
                    'ORDER BY p.id')
                res = cr.fetchall()
                ids += map(lambda x:x[0], res)
        else: 
            if not len(ids):
                ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('default_code',operator,name)]+ args, limit=limit, context=context)
                ids += self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context)
        return result

product_product()
