# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#            
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import orm, fields


class payment_type(orm.Model):
    _inherit = 'payment.type'
    _columns = {
        'sepa_category_purpose': fields.selection(
            [('CORT', '[CORT] Transaction is related to settlement of a trade, eg a foreign exchange deal or a securities transaction.'),
             ('SALA', '[SALA] Transaction is the payment of salaries.'),
             ('TREA', '[TREA] Transaction is related to treasury operations. E.g. financial contract settlement.'),
             ('CASH', '[CASH] Transaction is a general cash management instruction.'),
             ('DIVI', '[DIVI] Transaction is the payment of dividends.'),
             ('GOVT', '[GOVT] Transaction is a payment to or from a government department.'),
             ('INTE', '[INTE] Transaction is the payment of interest.'),
             ('LOAN', '[LOAN] Transaction is related to the transfer of a loan to a borrower.'),
             ('PENS', '[PENS] Transaction is the payment of pension.'),
             ('SECU', '[SECU] Transaction is the payment of securities.'),
             ('SUPP', '[SUPP] Transaction is related to a payment to a supplier.'),
             ('TAXS', '[TAXS] Transaction is the payment of taxes.'),
             ('TRAD', '[TRAD] Transaction is related to the payment of a trade finance transaction.'),
             ('VATX', '[VATX] Transaction is the payment of value added tax.'),
             ('HEDG', '[HEDG] Transaction is related to the payment of a hedging operation.'),
             ('INTC', '[INTC] Transaction is an intra-company payment, ie, a payment between two companies belonging to the same group.'),
             ('WHLD', '[WHLD] Transaction is the payment of withholding tax.'),
            ],
            'SEPA Category Purpose Type', required=False, size=4,
            help="Select the appropiate SEPA category for transactions made under this payment type."
            " Only appplicable for SEPA Credit Transfers."
        ),
    }

    _defaults = {
        'sepa_category_purpose': 'SUPP',
        }
