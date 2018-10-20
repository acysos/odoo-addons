# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name" : "Purchase 3 Discounts",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "http://www.acysos.com",
    "category": "Generic Modules/Sales & Purchases",
    "license" : "AGPL-3",
    "depends" : [ 
        'account',
        'purchase',
        'purchase_discount',
    ], 
    "category" : "Generic Modules/Purchase",
    "init_xml" : [],
    "demo_xml" : [],
    "data" : ['views/purchase_view.xml',
              'views/account_invoice_view.xml',
              'report/report_purchaseorder.xml',
              'report/report_invoice.xml'],
    "images": ['static/description/banner.jpg'],
    "active": False,
    "installable": True
}

