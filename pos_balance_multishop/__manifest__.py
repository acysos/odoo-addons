# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "POS Balace Multishop",
    "version": "1.0",
    "depends": ["base", "point_of_sale"],
    "author": "Acysos S.L.",
    "website": "http://www.acysos.com",
    "category": "Point of sale",
    "complexity": "normal",
    "description": """
    Add multiple code for balance products for each shop
    """,
    "init_xml": [],
    'update_xml': [
                'security/ir.model.access.csv',
                'views/product_view.xml',
                'views/sale_view.xml',
                'wizard/update_balance_codes_view.xml'
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
