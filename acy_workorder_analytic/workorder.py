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
    
    def _get_analytic_account(self, cr, uid, context):
        name = self.pool.get('ir.sequence').get(cr, uid, 'workorder-analytic')
        print name
        #analytic_exist_id = self.pool.get('account.analytic.account').search(cr, uid, [('name','=','Proyecto 11')], context=context)
        if not name:
            return None
        analytic_id = self.pool.get('account.analytic.account').create(cr, uid, {'name':name},{'account.analytic.account':True})
        print analytic_id
        return analytic_id
    
    _columns = {
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=False, states={'draft': [('readonly', False)]}, required=False)
    }
    
    _defaults = {
        'analytic_id': _get_analytic_account,
    }
    
    def save_workorder(self, cr, uid, ids,name,partner_id,partner_workorder_id,date_appointment,date_work,date_delivery,sale_order_ids,project_ids,analytic_id, context={}):
        wo_exist_id = self.pool.get('workorder').search(cr, uid, [('name','=',name)], context=context)
        
        if  not wo_exist_id:
            wo_id = self.pool.get('workorder').create(cr, uid, {'name':name,'partner_id':partner_id,'partner_workorder_id':partner_workorder_id,'date_appointment':date_appointment,'date_work':date_work,'date_delivery':date_delivery,'sale_order_ids':sale_order_ids,'project_ids':project_ids,'analytic_id':analytic_id},{'workorder':True})
        
        self.write(cr, uid, ids, {'name':name,'partner_id':partner_id,'partner_workorder_id':partner_workorder_id,'date_appointment':date_appointment,'date_work':date_work,'date_delivery':date_delivery,'sale_order_ids':sale_order_ids,'project_ids':project_ids,'analytic_id':analytic_id})
        return {'value': {'id': wo_id,'analytic_id':analytic_id}}
    
workorder()

# Sale order
#class sale_order(osv.osv):
    #_inherit = 'sale.order'
    #_columns = {
        #'vehicle_id': fields.related('workorder_id', 'vehicle_id', type='many2one', relation='res.partner.vehicle', string='Vehicle'),
    #}
#sale_order()