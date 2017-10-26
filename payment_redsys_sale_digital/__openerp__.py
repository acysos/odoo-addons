# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Redsys Payment Acquirer - Sale Digital",
    "version": "0.0.0.1",
    'category': 'Hidden',
    'summary': 'Payment Acquirer: if exist add downloable documents',
    "website": "https://www.acysos.com",
    "author": "Acysos S.L.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale_digital"
    ],
    "data": [
        "views/redsys.xml"
    ],
}