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
        'extra_parent_line_id': fields.many2one('account.invoice.line', 'Extra Price', help='The line that contain the product with the extra price'),
        'extra_child_line_id': fields.many2one('account.invoice.line', 'Line extra price', help=''),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of invoice lines."),
    }
    
    _order = 'sequence, id desc'
    
    _defaults = {
        'sequence': 10,
    }
account_invoice_line()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def create(self, cr, uid, vals, context=None):
        res = super(account_invoice, self).create(cr, uid, vals, context)
        self.expand_extra_prices(cr, uid, [res], context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_invoice,self).write(cr, uid, ids, vals, context)
        self.expand_extra_prices(cr, uid, ids, context)
        return res
    
    def expand_extra_prices(self, cr, uid, ids, context={}):
        if type(ids) in [int, long]:
            ids = [ids]
        updated_invoices = []
        for invoice in self.browse(cr, uid, ids, context):
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
                if line.product_id.extra_price == 0:
                    continue
                if line.extra_child_line_id:
                    continue
                
                sequence += 1
                tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, line.product_id.taxes_id)
                vals = {
                    'name': '--> '+(line.product_id.name_extra_price or ''),
                    'origin': line.origin,
                    'invoice_id': line.invoice_id.id,
                    'uos_id': line.uos_id.id,
                    'account_id': line.account_id.id,
                    'price_unit': line.product_id.extra_price,
                    'quantity': line.quantity,
                    'discount': line.discount,
                    'invoice_line_tax_id': [(6,0,tax_ids)],
                    'note': line.note,
                    'account_analytic_id': line.account_analytic_id.id or None,
                    'company_id': line.company_id.id,
                    'partner_id': line.partner_id.id,
                    'extra_parent_line_id': line.id,
                    'sequence': sequence
                }
                extra_line = self.pool.get('account.invoice.line').create(cr, uid, vals, context)
                if not invoice.id in updated_invoices:
                    updated_invoices.append( invoice.id )

                self.pool.get('account.invoice.line').write(cr,uid,[line.id],{'extra_child_line_id':extra_line})

                for id in reorder:
                    sequence += 1
                    self.pool.get('account.invoice.line').write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)
        return
    
    def _refund_cleanup_lines(self, cr, uid, lines):
        lines2 = []
        for line in lines:
            if line.has_key('extra_parent_line_id') and line.has_key('extra_child_line_id'):
                if line['extra_parent_line_id'] == False and line['extra_child_line_id'] == False:
                    lines2.append(line)
            else:
                lines2.append(line)
        
        for line in lines2:
            del line['id']
            del line['invoice_id']
            for field in ('company_id', 'partner_id', 'account_id', 'product_id',
                        'uos_id', 'account_analytic_id', 'tax_code_id', 'base_code_id'):
                line[field] = line.get(field, False) and line[field][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = [(6,0, line.get('invoice_line_tax_id', [])) ]
        return map(lambda x: (0,0,x), lines2)
    
account_invoice()