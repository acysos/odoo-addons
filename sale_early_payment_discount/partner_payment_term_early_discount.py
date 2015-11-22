# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

class account_partner_payment_term_early_discount(osv.osv):
    """Objeto que une las empresas con plazos de pago y descuentos pronto pago"""

    _name = "account.partner.payment.term.early.discount"
    _description = "Early payment discounts"

    def _get_default_partner(self, cr, uid, context):
        """return id of active object if it is res.partner"""
        if context.get('partner_id', False):
            return int(context['partner_id'])
        return False

    def _get_default_payment_term(self, cr, uid, context):
        """return id of active object if it is account.payment.term"""
        if context.get('payment_term', False):
            return int(context['payment_term'])
        return False

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
        'early_payment_discount': fields.float('E.P. disc.(%)', digits=(16,2), required=True, help="Percentage of discount for early payment.")
    }

    _defaults = {
        'partner_id': _get_default_partner,
        'payment_term_id': _get_default_payment_term
    }

account_partner_payment_term_early_discount()