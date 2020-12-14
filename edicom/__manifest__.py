# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Edicom",
    "version": "8.0.0.0.1",
    "author": "Domatix, Acysos S.L.",
    "website": "http://www.domatix.com, http://www.acysos.com",
    "category": "Generic Modules/Others",
    "description": """
        Generación e importación de ficheros de intercambio de Edicom
    """,
    "license": "AGPL-3",
    "depends": [
        'base',
        'stock',
        'sale',
        'l10n_es',
        'l10n_es_account_invoice_sequence',
        'product_supplierinfo_for_customer',
        'account_invoice_triple_discount',
        'account_global_discount',
        'product_multi_ean',
        'product_multi_ean_partner'
    ],
    'data': [
        'security/edicom_security.xml',
        'views/edicom_invoice_view.xml',
        'views/invoice_view.xml',
        'views/account_view.xml',
        'views/company_view.xml',
        'views/partner_view.xml',
        'security/ir.model.access.csv',
        'views/edicom_delivery_alert_view.xml',
        'views/stock_picking_view.xml',
        'views/product_view.xml',
        'views/product_template_view.xml',
        'data/ir_sequence.xml'
        ],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
