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
from datetime import datetime, date

# Word order
class workorder(osv.osv):
    _description = 'Work Order'
    _name = 'workorder'
    
    _columns = {
        'name': fields.char('Work Order Reference', size=64, readonly=False, required=True, select=True),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=False, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True),
	    'partner_workorder_id': fields.many2one('res.partner.address', 'Address', readonly=False, required=True, states={'draft': [('readonly', False)]}, help="The name and address of the contact that requested the workorder."),
        'sale_order_ids': fields.one2many('sale.order', 'workorder_id', 'Sale orders'),
        'project_ids': fields.one2many('project.project', 'workorder_id', 'Projects'),
        'date_created': fields.date('Created Date'),
        'date_appointment': fields.date('Appointment Date'),
        'date_work': fields.date('Work Date'),
        'date_delivery': fields.date('Delivery Date'),
        'number_sale_orders': fields.integer('Number Sale Orders'),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=False, select=True),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'workorder'),
        'number_sale_orders': lambda *a: 0,
        'date_created': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Code of the Workorder must be unique !')
    ]
    
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value': {'partner_workorder_id': False}}

        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery', 'invoice', 'contact'])

        val = {
            'partner_workorder_id': addr['contact'],
        }

        return {'value': val}
    
    def copy(self, cr, uid, id, default=None, context={}):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'workorder'),
        })
        return super(workorder, self).copy(cr, uid, id, default, context)
    
    def save_workorder(self, cr, uid, ids,name,partner_id,partner_workorder_id,date_appointment,date_work,date_delivery,sale_order_ids,project_ids, context={}):
        wo_exist_id = self.pool.get('workorder').search(cr, uid, [('name','=',name)], context=context)
        
        if  not wo_exist_id:
            wo_id = self.pool.get('workorder').create(cr, uid, {'name':name,'partner_id':partner_id,'partner_workorder_id':partner_workorder_id,'date_appointment':date_appointment,'date_work':date_work,'date_delivery':date_delivery,'sale_order_ids':sale_order_ids,'project_ids':project_ids},{'workorder':True})
        
        self.write(cr, uid, ids, {'name':name,'partner_id':partner_id,'partner_workorder_id':partner_workorder_id,'date_appointment':date_appointment,'date_work':date_work,'date_delivery':date_delivery,'sale_order_ids':sale_order_ids,'project_ids':project_ids})
        return {'value': {'id': wo_id}}
        
    def create(self, cr, uid, vals, context=None):
        if context.get('workorder', False):
            return super(workorder,self).create(cr, uid, vals, context)
        else:
            sql = "SELECT workorder.id FROM workorder WHERE name = '%s'" % (vals.get('name'))
            cr.execute(sql)
            ids = cr.fetchone()[0]
            super(workorder,self).write(cr, uid, ids, vals, context={})
            return ids
    
workorder()

# Project
class project_project(osv.osv):
    _inherit = 'project.project'
    _columns = {
        'workorder_id': fields.many2one('workorder', 'Work Order', readonly=True, required=False, select=True),
    }
project_project()