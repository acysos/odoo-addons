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

"""Inherit purchase_order to add early payment discount"""

from osv import fields, osv
import decimal_precision as dp

class purchase_order(osv.osv):
    """Inherit purchase_order to add early payment discount"""

    _inherit = "purchase.order"

    def _amount_all2(self, cr, uid, ids, field_name, arg, context):
        """calculates functions amount fields"""
        res = {}

        for order in self.browse(cr, uid, ids):
            res[order.id] = {
                'early_payment_disc_untaxed': 0.0,
                'early_payment_disc_tax': 0.0,
                'early_payment_disc_total': 0.0,
                'total_early_discount': 0.0
            }

            if not order.early_payment_discount:
                res[order.id]['early_payment_disc_total'] = order.amount_total
                res[order.id]['early_payment_disc_tax'] = order.amount_tax
                res[order.id]['early_payment_disc_untaxed'] = order.amount_untaxed
            else:
                res[order.id]['early_payment_disc_tax'] = order.amount_tax * (1.0 - (float(order.early_payment_discount or 0.0)) / 100.0)
                res[order.id]['early_payment_disc_untaxed'] = order.amount_untaxed * (1.0 - (float(order.early_payment_discount or 0.0)) / 100.0)
                res[order.id]['early_payment_disc_total'] = res[order.id]['early_payment_disc_untaxed'] + res[order.id]['early_payment_disc_tax']
                res[order.id]['total_early_discount'] = res[order.id]['early_payment_disc_untaxed'] - order.amount_untaxed

        return res

    def _get_order(self, cr, uid, ids, context={}):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'early_payment_discount': fields.float('E.P. disc.(%)', digits=(16, 2), help="Early payment discount"),
        'early_payment_disc_total': fields.function(_amount_all2, method=True, digits_compute=dp.get_precision('Account'), string='With E.P.',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'early_payment_discount'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='epd'),
        'early_payment_disc_untaxed': fields.function(_amount_all2, method=True, digits_compute=dp.get_precision('Account'), string='Untaxed Amount E.P.',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'early_payment_discount'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='epd'),
        'early_payment_disc_tax': fields.function(_amount_all2, method=True, digits_compute=dp.get_precision('Account'), string='Taxes E.P.',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'early_payment_discount'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='epd'),
        'total_early_discount': fields.function(_amount_all2, method=True, digits_compute=dp.get_precision('Account'), string='E.P. amount',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'early_payment_discount'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='epd'),
    }

    def onchange_partner_id2(self, cr, uid, ids, part,
                             early_payment_discount=False, payment_term=False):
        """ Extend this event for delete early payment discount if it isn't
            valid to new partner or add new early payment discount
        """
        res = self.onchange_partner_id(cr, uid, ids, part)
        if not res['value']['partner_address_id']:
            res['value']['payment_term'] = False
            res['value']['early_payment_discount'] = False
            return res

        if payment_term != res['value'].get('payment_term', False):
            payment_term = res['value']['payment_term']

        discount = self.onchange_payment_term(cr, uid, ids, payment_term, part)
        res['value']['early_payment_discount'] = discount['value']\
                                                ['early_payment_discount']
        return res

    def onchange_payment_term(self, cr, uid, ids, payment_term, part=False):
        """ On change event to update early payment dicount when the payment 
            term changes
        """

        early_discount_obj = self.pool.get('account.partner.purchase.payment.'\
                                           'term.early.discount')
        early_discs = []
        res = {}
        if payment_term:
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

    def action_invoice_create(self, cr, uid, ids, context=None):
        """
            Inherited method for writing early_payment_discount value in
            created invoice
        """
        invoice_id = super(purchase_order, self).action_invoice_create(
                                                        cr, uid, ids, 
                                                        context=context)
        invoice_obj = self.pool.get('account.invoice')
        current_purchase = self.browse(cr, uid, ids)[0]
        if current_purchase.early_payment_discount:
            values = {
                'early_payment_discount': current_purchase.\
                                                        early_payment_discount,
                'payment_term': current_purchase.payment_term.id,
            }
            invoice_obj.write(cr, uid, invoice_id, values)
        return invoice_id


purchase_order()
