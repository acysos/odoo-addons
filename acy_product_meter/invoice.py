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
#############################################################################

import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'meter_parent_line_id': fields.many2one('account.invoice.line', 'Parent line product meter', help='The line that contain the product with meters'),
        'meter_child_line_id': fields.many2one('account.invoice.line', 'Child line product meter'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of invoice lines."),
        'meter_line': fields.many2one('product.meter','Product Meter'),
    }
    
    _order = 'sequence, id desc'
    
    _defaults = {
        'sequence': 10,
    }
account_invoice_line()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        try:
            res = super(account_invoice, self).create(cr, uid, vals, context)
            for inv_id, name in self.name_get(cr, uid, [res], context=context):
                ctx = context.copy()
                if vals.get('type', 'in_invoice') in ('out_invoice', 'out_refund'):
                    ctx = self.get_log_context(cr, uid, context=ctx)
                message = _("Invoice '%s' is waiting for validation.") % name
                self.log(cr, uid, inv_id, message, context=ctx)
            self.expand_product_meters(cr, uid, [res], context)
            return res
        except Exception, e:
            if '"journal_id" viol' in e.args[0]:
                raise orm.except_orm(_('Configuration Error!'),
                     _('There is no Accounting Journal of type Sale/Purchase defined!'))
            else:
                raise orm.except_orm(_('Unknown Error'), str(e))
    
    def write(self, cr, uid, ids, vals, context=None):
        self.expand_product_meters(cr, uid, ids, context)
        res = super(account_invoice,self).write(cr, uid, ids, vals, context)
        return res
    
    def expand_product_meters(self, cr, uid, ids, context={}):
        if not context:
            context = {}
        if type(ids) in [int, long]:
            ids = [ids]
        updated_invoices = []
        for invoice in self.browse(cr, uid, ids, context):
            context['lang'] = invoice.partner_id.lang
            fiscal_position = invoice.fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, invoice.fiscal_position.id, context) or False
            
            sequence = -1
            reorder = []
            for line in invoice.invoice_line:
                sequence += 1
                if sequence > line.sequence:
                    self.pool.get('account.invoice.line').write(cr, uid, [line.id], {
                        'sequence': sequence,
                    }, context)
                else:
                    sequence = line.sequence

                #if line.state != 'draft':
                    #continue
                if not line.product_id:
                    continue
                if line.product_id.meters == 0:
                    continue
                if line.meter_child_line_id:
                    continue
                
                sequence += 1
                tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, line.product_id.taxes_id)
                if line.invoice_id.date_invoice:
                    date_search = line.invoice_id.date_invoice
                else:
                    date_search = time.strftime('%Y-%m-%d')
                meter_object = self.pool.get('product.meter')
                new_meter_id = meter_object.search(cr, uid, [('product_id','=',line.product_id.id),('partner_id','=',line.invoice_id.partner_id.id),('state','=','read'),('date','<=',date_search)], order='date', context=context)
                if not new_meter_id:
                    if invoice.state == 'draft': continue
                    else: raise osv.except_osv(_('Error!'), _('Not found actual meter %s %s') % (invoice.partner_id.name, line.product_id.name))
                new_meter = meter_object.browse(cr,uid,new_meter_id[0], context=context)

                last_meter_id = meter_object.search(cr, uid, [('product_id','=',line.product_id.id),('partner_id','=',line.invoice_id.partner_id.id),('state','=','invoiced'),('date','<',new_meter.date)], order='date desc', context=context)
                if not last_meter_id:
                    if invoice.state == 'draft': continue
                    else: raise osv.except_osv(_('Error!'), _('Not found previous meter %s %s') % (invoice.partner_id.name, line.product_id.name))
                last_meter = meter_object.browse(cr,uid,last_meter_id[0], context=context)
                
                line_description = line.product_id.meter_description
                line_description = line_description.replace('[last]',str(last_meter.meter))
                line_description = line_description.replace('[new]',str(new_meter.meter))
                
                vals = {
                    'name': '--> '+line_description or ' ',
                    'origin': line.origin,
                    'invoice_id': line.invoice_id.id,
                    'uos_id': line.uos_id.id,
                    'account_id': line.account_id.id,
                    'price_unit': 0,
                    'quantity': 0,
                    'discount': 0,
                    'invoice_line_tax_id': [(6,0,tax_ids)],
                    'note': line.note,
                    'account_analytic_id': line.account_analytic_id.id or None,
                    'company_id': line.company_id.id,
                    'partner_id': line.partner_id.id,
                    'meter_parent_line_id': line.id,
                    'sequence': sequence
                }
                meter_line = self.pool.get('account.invoice.line').create(cr, uid, vals, context)

                if not invoice.id in updated_invoices:
                    updated_invoices.append( invoice.id )
                
                self.pool.get('account.invoice.line').write(cr,uid,[line.id],{'meter_child_line_id':meter_line, 'quantity':(new_meter.meter - last_meter.meter),'meter_line':new_meter.id})

                for id in reorder:
                    sequence += 1
                    self.pool.get('account.invoice.line').write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)

        return
    
    def action_product_meter(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            for line in inv.invoice_line:
                if line.product_id.meters == 1:
                    self.pool.get('product.meter').write(cr,uid,[line.meter_line.id],{'state':'invoiced'})
        return True
                
    def action_cancel_product_meter(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            for line in inv.invoice_line:
                if line.product_id.meters == 1:
                    self.pool.get('product.meter').write(cr,uid,[line.meter_line.id],{'state':'read'})
        return True
    
account_invoice()