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
import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"

    def _get_analytic_lines(self, cr, uid, id):
        inv = self.browse(cr, uid, [id])[0]
        cur_obj = self.pool.get('res.currency')
        invoice_line_obj = self.pool.get('account.invoice.line')
        acct_ins_obj = self.pool.get('account.analytic.plan.instance')
        company_currency = inv.company_id.currency_id.id
        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1

        iml = invoice_line_obj.move_line_get(cr, uid, inv.id)

        for il in iml:
            if il.get('analytics_id', False):

                if inv.type in ('in_invoice', 'in_refund'):
                    ref = inv.reference
                else:
                    ref = self._convert_ref(cr, uid, inv.number)
                obj_move_line = acct_ins_obj.browse(cr, uid, il['analytics_id'])
                amount_vat = il['price']
                for tax in il['taxes']:
                    amount_vat += il['price'] * tax.amount
                amount_calc = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, amount_vat, context={'date': inv.date_invoice}) * sign
                qty = il['quantity']
                il['analytic_lines'] = []
                for line2 in obj_move_line.account_ids:
                    amt = amount_calc * (line2.rate/100)
                    qtty = qty* (line2.rate/100)
                    al_vals = {
                        'name': il['name'],
                        'date': inv['date_invoice'],
                        'unit_amount': qtty,
                        'product_id': il['product_id'],
                        'account_id': line2.analytic_account_id.id,
                        'amount': amt,
                        'product_uom_id': il['uos_id'],
                        'general_account_id': il['account_id'],
                        'journal_id': self._get_journal_analytic(cr, uid, inv.type),
                        'ref': ref,
                    }
                    il['analytic_lines'].append((0, 0, al_vals))
        return iml

account_invoice()

class account_move_line(osv.osv):

    _inherit = "account.move.line"
    _name = "account.move.line"
    
    def create_analytic_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        super(account_move_line, self).create_analytic_lines(cr, uid, ids, context=context)
        analytic_line_obj = self.pool.get('account.analytic.line')
        for line in self.browse(cr, uid, ids, context=context):
           if line.analytics_id:
               if not line.journal_id.analytic_journal_id:
                   raise osv.except_osv(_('No Analytic Journal !'),_("You have to define an analytic journal on the '%s' journal!") % (line.journal_id.name,))

               toremove = analytic_line_obj.search(cr, uid, [('move_id','=',line.id)], context=context)
               if toremove:
                    analytic_line_obj.unlink(cr, uid, toremove, context=context)
               for line2 in line.analytics_id.account_ids:
                   val = (line.credit or  0.0) - (line.debit or 0.0)
                   amt=val * (line2.rate/100)
                   al_vals={
                       'name': line.name,
                       'date': line.date,
                       'account_id': line2.analytic_account_id.id,
                       'unit_amount': line.quantity,
                       'product_id': line.product_id and line.product_id.id or False,
                       'product_uom_id': line.product_uom_id and line.product_uom_id.id or False,
                       'amount': amt,
                       'general_account_id': line.account_id.id,
                       'move_id': line.id,
                       'journal_id': line.journal_id.analytic_journal_id.id,
                       'ref': line.ref,
                       'percentage': line2.rate,
                   }
                   analytic_line_obj.create(cr, uid, al_vals, context=context)
        return True
    
account_move_line()