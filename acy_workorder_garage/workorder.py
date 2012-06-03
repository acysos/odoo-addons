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

# Word order
class workorder(osv.osv):
    _inherit = 'workorder'
    
    _columns = {
        'vehicle_id': fields.many2one('res.partner.vehicle', 'Vehicle', readonly=False, states={'draft': [('readonly', False)]}, required=True),
	    'km': fields.char('Kilometres', size=128, required=False),
    }
    
    def save_workorder(self, cr, uid, ids,name,partner_id,partner_workorder_id,date_appointment,date_work,date_delivery,sale_order_ids,project_ids,vehicle_id,km, context={}):
        wo_exist_id = self.pool.get('workorder').search(cr, uid, [('name','=',name)], context=context)
        
        if  not wo_exist_id:
            wo_id = self.pool.get('workorder').create(cr, uid, {'name':name,'partner_id':partner_id,'partner_workorder_id':partner_workorder_id,'date_appointment':date_appointment,'date_work':date_work,'date_delivery':date_delivery,'sale_order_ids':sale_order_ids,'project_ids':project_ids,'vehicle_id':vehicle_id,'km':km},{'workorder':True})
        
        self.write(cr, uid, ids, {'name':name,'partner_id':partner_id,'partner_workorder_id':partner_workorder_id,'date_appointment':date_appointment,'date_work':date_work,'date_delivery':date_delivery,'sale_order_ids':sale_order_ids,'project_ids':project_ids,'vehicle_id':vehicle_id,'km':km})
        return {'value': {'id': wo_id}}
    
workorder()

# Sale order
class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'vehicle_id': fields.related('workorder_id', 'vehicle_id', type='many2one', relation='res.partner.vehicle', string='Vehicle'),
    }
sale_order()