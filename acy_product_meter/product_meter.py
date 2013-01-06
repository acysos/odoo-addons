# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

class product_meters_page(osv.osv):
    _name = "product.meters.page"
    _description = "Product Meters Page"
    
    _columns = {
        'name': fields.char('Name', size=64, readonly=False, required=True),
        'date': fields.date('Date',select=True,required=True, states={'confirm': [('readonly', True)]}),
        'product_id': fields.many2one('product.product', 'Product', select=True, required=True, states={'confirm': [('readonly', True)]}),
        'meter_state': fields.selection([('read', 'Read'),('invoiced', 'Invoiced')], 'Meters State', required=True, states={'confirm': [('readonly', True)]}),
        'product_meters': fields.one2many('product.meter','product_meters_page_id', 'Product Meters', states={'draft':[('readonly',False)]}, readonly=True),
        'state': fields.selection([('draft', 'Draft'),('confirmed', 'Confirmed')], 'State', required=True, readonly=True),
    }
    
    _defaults = {
        'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'product.meter.page'),
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'meter_state': 'read',
        'state': 'draft',
    }
    
    def onchange_date(self, cr, uid, ids, date, context=None):
        if date:
            for id in ids:
                page = self.pool.get('product.meters.page').browse(cr,uid,id,context)
                for meter in page.product_meters:
                    self.pool.get('product.meter').write(cr,uid,meter.id,{'date':date})
        return {'date': date}
                
    def onchange_meter_state(self, cr, uid, ids, meter_state, context=None):
        if meter_state:
            for id in ids:
                page = self.pool.get('product.meters.page').browse(cr,uid,id,context)
                for meter in page.product_meters:
                    self.pool.get('product.meter').write(cr,uid,meter.id,{'state':meter_state})
        return {'meter_state': meter_state}
                
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if product_id:
            for id in ids:
                page = self.pool.get('product.meters.page').browse(cr,uid,id,context)
                for meter in page.product_meters:
                    self.pool.get('product.meter').write(cr,uid,meter.id,{'product_id':product_id})
        return {'product_id': product_id}
    
    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        context['meter_state'] = 'read'
        context['date'] = time.strftime('%Y-%m-%d')
        default.update({
            'state': 'draft',
            'meter_state': 'read',
            'date': time.strftime('%Y-%m-%d'),
        })
        return super(product_meters_page, self).copy(cr, uid, id, default, context=context)
    
product_meters_page()

class product_meter(osv.osv):
    _name = "product.meter"
    _description = "Product Meter"
    
    _columns = {
        'name': fields.char('Name', size=64, readonly=True, required=True),
        'date': fields.date('Date', select=1),
        'partner_id': fields.many2one('res.partner', 'Partner', select=True, required=True),
        'product_id': fields.many2one('product.product', 'Product', select=True, required=True),
        'meter': fields.float('Meter', digits_compute=dp.get_precision('Decimal Meter')),
        'state': fields.selection([('read', 'Read'),('invoiced', 'Invoiced')], 'State', required=True, readonly=True),
        'product_meters_page_id': fields.many2one('product.meters.page', 'Product Meters Page', ondelete='cascade'),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'product.meter'),
        'date': lambda self, cr, uid, context : context['date'] if context and 'date' in context else time.strftime('%Y-%m-%d'),
        'product_id' : lambda self, cr, uid, context : context['product_id'] if context and 'product_id' in context else None,
        'state' : lambda self, cr, uid, context : context['meter_state'] if context and 'meter_state' in context else 'read',
    }
    
    _order = 'date desc'
    
    _sql_constraints = [
        ('meter_uniq', 'unique(date, partner_id, product_id)', 'Only one meter per day, per partner and per product !'),
    ]
    
    def action_read(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'read'})
        return True
    
    def action_invoiced(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'invoiced'})
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': time.strftime('%Y-%m-%d'),
            'state': 'read',
        })
        return super(product_meter, self).copy(cr, uid, id, default, context=context)
        
    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': time.strftime('%Y-%m-%d'),
            'state': 'read',
        })
        return super(product_meter, self).copy_data(cr, uid, id, default, context=context)
    
product_meter()