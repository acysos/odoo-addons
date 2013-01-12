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
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of invoice lines."),
        'compute': fields.boolean('Compute'),
    }
    
    _order = 'sequence, id desc'
    
    _defaults = {
        'sequence': 10,
        'compute': True,
    }

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            if line.compute == True:
                mres = self.move_line_get_item(cr, uid, line, context)
                if not mres:
                    continue
                res.append(mres)
                tax_code_found= False
                for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                        (line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),
                        line.quantity, inv.address_invoice_id.id, line.product_id,
                        inv.partner_id)['taxes']:
    
                    if inv.type in ('out_invoice', 'in_invoice'):
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
    
                    if tax_code_found:
                        if not tax_code_id:
                            continue
                        res.append(self.move_line_get_item(cr, uid, line, context))
                        res[-1]['price'] = 0.0
                        res[-1]['account_analytic_id'] = False
                    elif not tax_code_id:
                        continue
                    tax_code_found = True
    
                    res[-1]['tax_code_id'] = tax_code_id
                    res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
        return res

account_invoice_line()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _amount_all_compute(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.invoice_line:
                if line.compute == True:
                    res[invoice.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res
                
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
                
    _columns = {
        'amount_untaxed': fields.function(_amount_all_compute, method=True, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all_compute, method=True, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all_compute, method=True, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
    }
    
    def create(self, cr, uid, vals, context=None):
        res = super(account_invoice, self).create(cr, uid, vals, context)
        self.group_by_product(cr, uid, [res], context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_invoice,self).write(cr, uid, ids, vals, context)
        self.group_by_product(cr, uid, ids, context)
        return res
    
    def group_by_product(self, cr, uid, ids, context={}):
        if type(ids) in [int, long]:
            ids = [ids]
        inv_line_obj = self.pool.get('account.invoice.line')
        product_group = {}
        for invoice in self.browse(cr, uid, ids, context):
            for line in invoice.invoice_line:
                if line.compute == True:
                    if not invoice.id in product_group:
                        product_group[invoice.id] = {'products':{},'sequence': 1}
                    if not line.product_id.id:
                        inv_line_obj.write(cr, uid, [line.id], {'sequence': 0}, context=context)
                    else:
                        if line.product_id.id in product_group[invoice.id]['products']:
                            product_group[invoice.id]['products'][line.product_id.id][0] += line.quantity
                            product_group[invoice.id]['products'][line.product_id.id][1] += line.price_subtotal
                            inv_line_obj.write(cr, uid, [line.id], {'sequence': product_group[invoice.id]['products'][line.product_id.id][2]}, context=context)
                        else:
                            product_group[invoice.id]['products'][line.product_id.id] = [line.quantity,line.price_subtotal,product_group[invoice.id]['sequence'],line.account_id.id]
                            inv_line_obj.write(cr, uid, [line.id], {'sequence': product_group[invoice.id]['sequence']}, context=context)
                            product_group[invoice.id]['sequence'] += 2
            
        for invoice_id_gr, values_inv in product_group.iteritems():
            for product_id, values_pro in values_inv['products'].iteritems():
                group_line_id = inv_line_obj.search(cr,uid,[('invoice_id','=',invoice_id_gr),('product_id','=',product_id),('compute','=',False)])
                if not group_line_id:
                    product = self.pool.get('product.product').browse(cr,uid,product_id,context)
                    invoice_line_id = inv_line_obj.create(cr, uid, {
                        'name': '--> '+product.default_code+' '+product.name,
                        'invoice_id': invoice_id_gr,
                        'uos_id': product.uos_id.id,
                        'product_id': product.id,
                        'account_id': values_pro[3],
                        'price_unit': values_pro[1]/values_pro[0],
                        'discount': 0,
                        'quantity': values_pro[0],
                        'sequence': values_pro[2]+1,
                        'compute': False,
                    }, context=context)
                else:
                    inv_line_obj.write(cr,uid,group_line_id,{'quantity': values_pro[0],'price_unit': values_pro[1]/values_pro[0]})
        return
    
account_invoice()

class account_invoice_tax(osv.osv):
    _inherit = "account.invoice.tax"
    
    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            if line.compute == True:
                for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id)['taxes']:
                    val={}
                    val['invoice_id'] = inv.id
                    val['name'] = tax['name']
                    val['amount'] = tax['amount']
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = tax['price_unit'] * line['quantity']
    
                    if inv.type in ('out_invoice','in_invoice'):
                        val['base_code_id'] = tax['base_code_id']
                        val['tax_code_id'] = tax['tax_code_id']
                        val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                        val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                        val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    else:
                        val['base_code_id'] = tax['ref_base_code_id']
                        val['tax_code_id'] = tax['ref_tax_code_id']
                        val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                        val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                        val['account_id'] = tax['account_paid_id'] or line.account_id.id
    
                    key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                    if not key in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
                        tax_grouped[key]['base_amount'] += val['base_amount']
                        tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped
        
account_invoice_tax()
