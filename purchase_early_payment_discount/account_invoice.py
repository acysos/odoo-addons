# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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

"""Inherit account_invoice to compute from button the early payment discount"""

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp

def intersect(la, lb):
    """returns True for equal keys in two lists"""
    l = filter(lambda x: x in lb, la)
    return len(l) == len(la) == len(lb)

class account_invoice(osv.osv):
    """Inherit account_invoice to compute from button the early payment discount"""

    _inherit = 'account.invoice'

    def _get_early_discount_amount(self, cr, uid, ids, field_name, arg, context):
        """obtain early_payment_discount_amount"""
        res = {}
        prod_early_payment_id = self.pool.get('product.product').search(cr, uid, [('default_code', '=', 'DPP')])
        prod_early_payment_id = prod_early_payment_id and prod_early_payment_id[0] or False

        if prod_early_payment_id:
            for invoice in self.browse(cr, uid, ids):
                if not invoice.early_payment_discount:
                    res[invoice.id] = 0.0
                    continue
                #searches if DPP is applied
                found = False
                for line in invoice.invoice_line:
                    if line.product_id and line.product_id.id == prod_early_payment_id:
                        found = True
                        break;

                if found:
                    res[invoice.id] = 0.0
                else:
                    total_net_price = 0.0
                    for invoice_line in invoice.invoice_line:
                        total_net_price += invoice_line.price_subtotal

                    res[invoice.id] = float(total_net_price) - (float(total_net_price) * (1 - (invoice.early_payment_discount or 0.0) / 100.0))

        return res

    '''
    _columns = {
        'purchase_early_payment_discount': fields.float('E.P. disc.(%)', digits=(16, 2), help="Early payment discount"),
        'purchase_early_discount_amount': fields.function(_get_early_discount_amount, method=True, string="E.P. amount", type='float', digits_compute=dp.get_precision('Account'), help="Early payment discount amount to apply.", readonly=True)
    }
    '''

    def compute_early_payment_discount(self, cr, uid, invoice_line_ids, early_payment_percentage):
        """computes early payment price_unit"""
        total_net_price = 0.0

        for invoice_line in self.pool.get('account.invoice.line').browse(cr, uid, invoice_line_ids):
            total_net_price += invoice_line.price_subtotal

        return float(total_net_price) - (float(total_net_price) * (1 - (float(early_payment_percentage) or 0.0) / 100.0))

    def compute_early_payment_lines(self, cr, uid, id):
        """creates early payment lines"""
        invoice = self.browse(cr, uid, id)
        if 'out' in invoice.type:
            return super(account_invoice, self).compute_early_payment_lines(cr, uid, id)

        early_payments = {}
        inv_lines_out_vat = []
        for invoice_line in invoice.invoice_line:
            if invoice_line.invoice_line_tax_id:
                line_tax_ids = [x.id for x in invoice_line.invoice_line_tax_id]
                found = False

                for key in early_payments:
                    if intersect([int(x) for x in key.split(",")], line_tax_ids):
                        early_payments[key].append(invoice_line.id)
                        found = True
                        break;

                if not found:
                    tax_str = ",".join([str(x) for x in line_tax_ids])
                    early_payments[tax_str] = [invoice_line.id]
            else:
                #lines without vat defined
                inv_lines_out_vat.append(invoice_line.id)

        prod_early_payment = self.pool.get('product.product').browse(cr, uid, self.pool.get('product.product').search(cr, uid, [('default_code', '=', 'DPP')]))
        prod_early_payment = prod_early_payment and prod_early_payment[0] or False

        if prod_early_payment:
            group_account_line = {}
            for early_payment_line in early_payments:
                group_account_line[early_payment_line] = {}

                for invoice_line in self.pool.get('account.invoice.line').browse(cr, uid, early_payments[early_payment_line]):
                    if invoice_line.product_id.categ_id and invoice_line.product_id.categ_id.property_account_purchase_early_payment_disc and str(invoice_line.product_id.categ_id.property_account_purchase_early_payment_disc.id) not in group_account_line[early_payment_line]:
                        group_account_line[early_payment_line][str(invoice_line.product_id.categ_id.property_account_purchase_early_payment_disc.id)] = [invoice_line.id]
                    elif invoice_line.product_id.categ_id and invoice_line.product_id.categ_id.property_account_purchase_early_payment_disc and str(invoice_line.product_id.categ_id.property_account_purchase_early_payment_disc.id) in group_account_line[early_payment_line]:
                        group_account_line[early_payment_line][str(invoice_line.product_id.categ_id.property_account_purchase_early_payment_disc.id)].append(invoice_line.id)
                    elif prod_early_payment.property_stock_account_input and str(prod_early_payment.property_stock_account_input.id) not in group_account_line[early_payment_line]:
                        group_account_line[early_payment_line][str(prod_early_payment.property_stock_account_input.id)] = [invoice_line.id]
                    elif prod_early_payment.property_stock_account_input and str(prod_early_payment.property_stock_account_input.id) in group_account_line[early_payment_line] or prod_early_payment.categ_id.property_account_purchase_early_payment_disc.id and str(prod_early_payment.categ_id.property_account_purchase_early_payment_disc.id) in group_account_line[early_payment_line]:
                        group_account_line[early_payment_line][str(prod_early_payment.property_stock_account_input.id)].append(invoice_line.id)
                    else:
                        raise osv.except_osv(_('Warning'), _('Cannot set early payment discount because now is impossible find the early payment account. Review invoice products categories have defined early payment account by default or early payment discount product have defined an input account.'))


            for early_payment_line in group_account_line:
                for account_id in group_account_line[early_payment_line]:
                    self.pool.get('account.invoice.line').create(cr, uid, {
                        #'name': len(group_account_line) > 1 and _("Early payment disc. (%s)") % self.pool.get('account.tax').browse(cr, uid, int(early_payment_line)).name or _("Early payment disc. ") + str(invoice.early_payment_discount) + "%",
                        'name': _("Early payment discount") + " " + str(invoice.early_payment_discount) + "%",
                        'invoice_id': id,
                        'product_id': prod_early_payment.id,
                        'account_id': int(account_id),
                        'price_unit': 0.0 - (self.compute_early_payment_discount(cr, uid, group_account_line[early_payment_line][account_id], invoice.early_payment_discount)),
                        'quantity': 1,
                        'invoice_line_tax_id': [(6, 0, [int(x) for x in early_payment_line.split(',')])]
                        })


            if inv_lines_out_vat:
                self.pool.get('account.invoice.line').create(cr, uid, {
                        'name': _("Early payment discount") + " " + str(invoice.early_payment_discount) + "%",
                        'invoice_id': id,
                        'product_id': prod_early_payment.id,
                        'account_id': prod_early_payment.categ_id and prod_early_payment.categ_id.property_account_purchase_early_payment_disc.id or prod_early_payment.property_stock_account_input.id,
                        'price_unit': 0.0 - (self.compute_early_payment_discount(cr, uid, inv_lines_out_vat, invoice.early_payment_discount)),
                        'quantity': 1
                        })

        #recompute taxes
        self.button_compute(cr, uid, [id], set_total=(type in ('in_invoice', 'in_refund')))

        return True

    def button_compute_early_payment_disc(self, cr, uid, ids, context=None):
        """computes early payment discount in invoice"""
        if context == None: context = {}

        for invoice in self.browse(cr, uid, ids):
            if invoice.early_payment_discount:
                #create list with all early discount lines to delete, new early discount lines will be created
                orig_early_payment_lines = []
                #searches for early discount product
                product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', 'DPP')])
                early_payment = self.pool.get('product.product').browse(cr, uid, product_ids[0])

                for invoice_line in invoice.invoice_line:
                    if invoice_line.product_id.id == early_payment.id:
                        orig_early_payment_lines.append(invoice_line.id)

                if orig_early_payment_lines:
                    #delete old early payment lines
                    self.pool.get('account.invoice.line').unlink(cr, uid, orig_early_payment_lines)

                self.compute_early_payment_lines(cr, uid, invoice.id)
        return True

    def onchange_partner_id(self, cr, uid, ids, inv_type, part,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False):
        """ Extend this event for delete early payment discount if it isn't 
            valid to new partner or add new early payment discount
    """

        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids,
                                inv_type, part, date_invoice=date_invoice,
                                payment_term=payment_term,
                                partner_bank_id=partner_bank_id,
                                company_id=company_id)
        if 'out' in inv_type:
            return res

        if not part:
            res['value']['payment_term'] = False
            res['value']['early_payment_discount'] = False
            return res

        if payment_term != res['value'].get('payment_term', False):
            payment_term = res['value']['payment_term']

        discount = self.onchange_payment_term2(cr, uid, ids, payment_term,
                                               inv_type, part)
        res['value']['early_payment_discount'] = discount['value']\
                                                    ['early_payment_discount']
        return res

    def onchange_payment_term2(self, cr, uid, ids, payment_term, inv_type=False,
                                                                part=False):
        """ On change event to update early payment discount when the payment
            term changes"""

        if 'out' in inv_type:
            return self.onchange_payment_term(cr, uid, ids, payment_term, part)

        early_discount_obj = self.pool.get('account.partner.purchase.payment.'\
                                                        'term.early.discount')
        early_discs = []
        res = {}
        if payment_term:
            res['date_due'] = False
            early_discs = early_discount_obj.search(cr, uid, [
                                    ('partner_id', '=', part),
                                    ('payment_term_id', '=', payment_term)])
            if early_discs:
                res['early_payment_discount'] = early_discount_obj.browse(cr,
                                    uid, early_discs[0]).early_payment_discount
            else:
                early_discs = early_discount_obj.search(cr, uid, [
                                        ('partner_id', '=', False),
                                        ('payment_term_id', '=', payment_term)])
                if early_discs:
                    res['early_payment_discount'] = early_discount_obj.browse(
                                cr, uid, early_discs[0]).early_payment_discount
        if not early_discs:
            early_discs = early_discount_obj.search(cr, uid, [
                                              ('partner_id', '=', part),
                                              ('payment_term_id', '=', False)])
            if early_discs:
                res['early_payment_discount'] = early_discount_obj.browse(cr,
                                  uid, early_discs[0]).early_payment_discount
            else: # Search default discount for everbody
                early_discs = early_discount_obj.search(cr, uid, [
                                              ('partner_id', '=', False),
                                              ('payment_term_id', '=', False)])
                if early_discs:
                    res['early_payment_discount'] = early_discount_obj.browse(
                              cr, uid, early_discs[0]).early_payment_discount
                else: # Delete early payment discount if there isn't early discount
                    res['early_payment_discount'] = False
        return {'value': res}

account_invoice()
