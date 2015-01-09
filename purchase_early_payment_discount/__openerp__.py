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

{
    "name" : "Purchase early payment discount",
    "description" : """Allow set an early payment discount in purchase orders, invoices and picking lists. Includes:
        -A new purchase report overriding default Purchase Report.
        -A new product category: System Products (a new account for E.P. will be set here)
        -A new product for early payment discounts (an input stock account for discounts can be set here)
    """,
    "version" : "1.0",
    "author" : "Zikzakmedia SL, Pexego",
    "depends" : [
        "sale_early_payment_discount",
        "purchase_payment",
    ],
    "category" : "Payment",
    "init_xml" : [],
    "update_xml" : [
        'partner_purchase_payment_term_early_discount_view.xml',
        'partner_view.xml',
        'payment_term_view.xml',
        'purchase_view.xml',
        'account_invoice_view.xml',
        'purchase_report.xml',
        'product_category_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
