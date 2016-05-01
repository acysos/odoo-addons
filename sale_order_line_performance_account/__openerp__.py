# -*- coding: utf-8 -*-
# © 2016 Ignacio Ibeas - Acysos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale Order Line Performance Account",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "Acysos S.L.",
    "website": "http://www.acysos.com",
    "contributors": [
        "Ignacio Ibeas <ignacio@acysos.com>",
    ],
    "category": "Sales Management",
    "depends": [
        "sale",
        "account",
        "sale_order_line_performance"
    ],
    "data": ['views/account_invoice_view.xml',
             'views/report_invoice.xml'
    ],
    "installable": True,
}
