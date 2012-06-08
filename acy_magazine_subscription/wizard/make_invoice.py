# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Based in internetdomain module.
#                       Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
from tools.translate import _

import time

class make_invoice(osv.osv_memory):
    _name = 'magazine.make.invoice.wizard'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'price': fields.float('Price'),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account', required=True),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }

    _defaults = {
        'state': lambda *a: 'first',
    }

    def makeInvoices(self, cr, uid, ids, data, context={}):
        """Create invoice from renowel"""

        renewal_obj = self.pool.get('magazine.renewal')
        account_payment_term_obj = self.pool.get('account.payment.term')
        analytic_account_obj = self.pool.get('account.analytic.account')
        res_partner_obj = self.pool.get('res.partner')
        account_payment_term_obj = self.pool.get('account.payment.term')

        form = self.browse(cr, uid, ids[0])
        product = form.product_id

        for id in ids:
            renewal = renewal_obj.browse(cr, uid, id)

            partner = renewal.subscription_id.partner_id.id
            invoices = []

            curr_invoice = {
                'name': renewal.subscription_id.name+' ('+renewal.first_number+' / '+renewal.last_number+')',
                'partner_id': renewal.subscription_id.partner_id.id,
            }

            if renewal.subscription_id.partner_id.property_payment_term:
                pterm_list= account_payment_term_obj.compute(cr, uid,
                    renewal.subscription_id.partner_id.property_payment_term.id, value=1,
                    date_ref=time.strftime('%Y-%m-%d'))
                if pterm_list:
                    pterm_list = [line[0] for line in pterm_list]
                    pterm_list.sort()
                    curr_invoice['date_due'] = pterm_list[-1]

            values = self.pool.get('account.invoice').onchange_partner_id(cr, uid, [], 'out_invoice', renewal.subscription_id.partner_id.id)
            curr_invoice.update(values['value'])

            last_invoice = self.pool.get('account.invoice').create(cr, uid, curr_invoice)
            invoices.append(last_invoice)

            taxes = product.taxes_id
            tax = self.pool.get('account.fiscal.position').map_tax(cr, uid, renewal.subscription_id.partner_id.property_account_position, taxes)
            account_id = product.product_tmpl_id.property_account_income.id or product.categ_id.property_account_income_categ.id

            curr_line = {
                'price_unit': renewal.price_unit or form.price or product.lst_price,
                'quantity': 1,
                'invoice_line_tax_id': [(6,0,tax)],
                'invoice_id': last_invoice,
                'name': product.name,
                'product_id': product.id,
                'uos_id': product.uom_id.id,
                'account_id': account_id,
                'account_analytic_id': form.account_id.id,
            }

            self.pool.get('account.invoice.line').create(cr, uid, curr_line)

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
            
        mod_id = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')])[0]
        res_id = mod_obj.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = act_obj.read(cr, uid, res_id, [])
        act_win['domain'] = [('id','in',invoices),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')

        return act_win

make_invoice()
