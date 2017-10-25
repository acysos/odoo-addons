# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Redsys Payment Acquirer - Invoices",
    "version": "8.0.0.0.1",
    'category': 'Hidden',
    'summary': 'Payment Acquirer: if exist add invoices in result return',
    "website": "https://www.acysos.com",
    "author": "Acysos S.L.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "payment_redsys"
    ],
    "data": [
        "views/redsys.xml"
    ],
}