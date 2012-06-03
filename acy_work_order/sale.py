# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import tools
import os
import time

# Sale order
class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    _columns = {
        'workorder_id': fields.many2one('workorder', 'Work Order', readonly=False, required=False, select=True),
    }
    
    def Child_name_change (self, cr, uid, ids, name, default_name):
        if default_name:
            sql = "SELECT workorder.number_sale_orders FROM workorder WHERE name = '%s'" % (default_name)
            cr.execute(sql)
            number = cr.fetchone()[0]
            order_name = default_name + '-' + str(number)
            sql = "UPDATE workorder SET number_sale_orders=%i WHERE name='%s'" % (number+1,default_name)
            cr.execute(sql)
            return {'value': {'name': order_name}}
    
    def Child_id_change (self, cr, uid, ids, workorder_id, default_name, context={}):
        if default_name:
            sql = "SELECT workorder.id FROM workorder WHERE name = '%s'" % (default_name)
            cr.execute(sql)
            wo_exist_id = cr.fetchone()[0]
            if wo_exist_id:
                return {'value': {'workorder_id': wo_exist_id}}
            
sale_order()