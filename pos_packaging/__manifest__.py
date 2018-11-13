# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Pos packaging",
    "version": "11.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Alexander Ezquevo <alexander@acysos.com>', ],
    "category": "",
    "license": "AGPL-3",
    "description": """ When read a packaging barcode in pos add packaging products
    """,
    "depends": ["point_of_sale", "stock",    
    ],
    "data": ["views/pos_templates.xml",
    ],
    "images": ['static/description/banner.jpg'],
    "installable": True,
}
