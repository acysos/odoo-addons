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

from datetime import datetime
from osv import osv, fields
from tools.translate import _
import netsvc
import time
import tools

class mrp_operator_registry(osv.osv):
    _description = 'MRP Operator Registry'
    _name = 'mrp.operator.registry'
    
    _columns = {
        'name': fields.char('Reference', size=64, required=True, states={'draft':[('readonly',False)]}, readonly=True),
        'date': fields.date('Date', required=True, select=True, states={'draft':[('readonly',False)]}, readonly=True),
        'operator_id': fields.many2one('hr.employee', 'Operator', required=True, states={'draft':[('readonly',False)]}, readonly=True),
        'workcenter_lines': fields.one2many('mrp.workcenter.registry', 'operator_registry_id', 'MRP Workcenter Registry', states={'draft':[('readonly',False)]}, readonly=True),
        'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('cancel','Cancelled')],'State', readonly=True),
    }
    
    _defaults = {
        'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'operator_registry'),
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
    }
    
    def action_confirm(self, cr, uid, ids, context=None):
        registry = self.browse(cr,uid,ids,context)[0]
        for workcenter_line in registry.workcenter_lines:
            if workcenter_line.production_id.id:
                sql = "SELECT MAX(sequence) FROM mrp_production_workcenter_line WHERE production_id = %s" % (workcenter_line.production_id.id)
                cr.execute(sql)
                sequence = cr.fetchone()[0]
                prod_obj = self.pool.get('mrp.production')
                stock_obj = self.pool.get('stock.move')
                if workcenter_line.production_id.state in ['draft','picking_except','cancel','done']:
                    raise osv.except_osv(_('Error'), _("Can't make production if the Manufacturing order is %s") % (workcenter_line.production_id.state))
                if workcenter_line.product_id:
                    if not workcenter_line.workcenter_line_id:
                        raise osv.except_osv(_('Error'), _("Can't produce a product without Workcenter %s") % (workcenter_line.product_id.name))
                if workcenter_line.workcenter_line_id:
                    if not workcenter_line.product_id:
                        raise osv.except_osv(_('Error'), _("Can't use a workcenter without product %s") % (workcenter_line.workcenter_line_id.name))
                prod_obj.action_in_production(cr,uid,workcenter_line.production_id.id)
                if sequence == workcenter_line.workcenter_line_id.sequence:
                    if workcenter_line.go_product_qty > 0:
                        prod_obj.action_produce(cr, uid,workcenter_line.production_id.id,workcenter_line.go_product_qty,'consume_produce',context)
                        
                for workcenter_line2 in registry.workcenter_lines:
                    if workcenter_line.production_id.id == workcenter_line2.production_id.id:
                        if workcenter_line2.workcenter_line_id.sequence <= workcenter_line.workcenter_line_id.sequence:
                            if workcenter_line.de_product_qty > 0:
                                #mrp_routing_ids = self.pool.get('mrp.routing.workcenter').search(cr,uid,[('routing_id','=',workcenter_line2.production_id.routing_id.id)], order='sequence', context=context)
                                #for mrp_routing_id in mrp_routing_ids:
                                    #product_line_id = self.pool.get('mrp.production.product.line').search(cr, uid, [('production_id','=',workcenter_line2.production_id.id),('consumed_on','=',mrp_routing_id)], context=context)
                                    #print product_line_id
                                    #if len(product_line_id) == 1:
                                        #break
                                mrp_routing_id = self.pool.get('mrp.routing.workcenter').search(cr,uid,[('routing_id','=',workcenter_line2.production_id.routing_id.id),('workcenter_id','=',workcenter_line2.workcenter_id.id)], context=context)
                                
                                product_line_id = self.pool.get('mrp.production.product.line').search(cr, uid, [('production_id','=',workcenter_line2.production_id.id),('consumed_on','=',mrp_routing_id[0])], context=context)
                                
                                if len(product_line_id) > 0:
                                    product_line = self.pool.get('mrp.production.product.line').browse(cr, uid, product_line_id, context)[0]
                                    
                                    move_name = 'PROD:'+workcenter_line2.production_id.name
                                    
                                    stock_move_id = stock_obj.search(cr,uid,[('product_id','=',product_line.product_id.id),('state','=','assigned'),('name','=',move_name)],context=context)
        
                                    bom_id = self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',workcenter_line2.production_id.bom_id.id),('product_id','=',product_line.product_id.id),('consumed_on','=',mrp_routing_id[0])], context=context)
                                    bom = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context)[0]
                                    defective_qty = bom.product_qty*bom.product_efficiency*workcenter_line.de_product_qty
                                    context = {'operator_registry':1,'location_src':workcenter_line2.production_id.location_src_id.id}
                                    stock_obj.action_scrap(cr, uid,stock_move_id,defective_qty,4,context)
        
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
mrp_operator_registry()

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    
    def _number_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for line in self.browse(cr,uid,ids,context):
            res[line.id] = line.production_id.name +'-'+ str(line.sequence)
        return res
    
    _columns = {
        'number': fields.function(_number_get, method=True, store=True, type='char', size=64, string='Number', readonly=True),
    }
    
    _rec_name = "number"
    
    
mrp_production_workcenter_line()

class mrp_workcenter_registry_key(osv.osv):
    _name = 'mrp.workcenter.registry.key'
    _description = 'MRP Workcenter Registry Key'
    _columns = {
        'name': fields.char('Name', required=True, size=46, translate=True),
    }
    
mrp_workcenter_registry_key()

class mrp_workcenter_registry(osv.osv):
    _description = 'MRP Workcenter Registry'
    _name = 'mrp.workcenter.registry'
    
    _columns = {
        'key': fields.many2one('mrp.workcenter.registry.key','Key'),
        'workcenter_line_id': fields.many2one('mrp.production.workcenter.line', 'Workcenter'),
        'product_id': fields.many2one('product.product', 'Product'),
        'name': fields.char('Operation Code', size=64, required=True),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Resource'),
        'de_product_qty': fields.float('Defective Product Qty'),
        'go_product_qty': fields.float('Good Product Qty'),
        'date_start': fields.date('Date start'),
        'time_start': fields.time('Time start'),
        'date_stop': fields.date('Date stop'),
        'time_stop': fields.time('Time stop'),
        'note': fields.text('Notes'),
        'operator_registry_id': fields.many2one('mrp.operator.registry', 'Operator registry', ondelete='cascade'),
        'production_id': fields.many2one('mrp.production', 'Manufacturing Order', ondelete='set null'),
        'operator_id': fields.related('operator_registry_id', 'operator_id', type='many2one', relation='hr.employee', string='Operator'),
    }
    
    _defaults = {
        'name':'/',
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_stop': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def workcenter_line_change(self, cr, uid, ids,workcenter_line_id,context={}):
        if (workcenter_line_id):
            workcenter_line = self.pool.get('mrp.production.workcenter.line').browse(cr, uid, [workcenter_line_id], context)[0]
            return {'value': {'workcenter_line_id': workcenter_line.id,'product_id':workcenter_line.production_id.product_id.id,'name':workcenter_line.name,'workcenter_id':workcenter_line.workcenter_id.id,'production_id':workcenter_line.production_id.id}}
    
mrp_workcenter_registry()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    _columns = {
        'operator_ids': fields.one2many('mrp.workcenter.registry', 'production_id', 'Operator Registry'),
    }

mrp_production()

class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'
    
    _sql_constraints = [
        ('sequence_routing_uniq', 'unique (sequence,routing_id)', 'The sequence must be unique per routing !')
    ]
    
mrp_routing_workcenter()