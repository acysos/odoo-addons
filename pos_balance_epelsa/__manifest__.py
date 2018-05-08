# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Epelsa Balances",
    "version": "1.0",
    "depends": ["base", "pos_balance_multishop"],
    "author": "Acysos S.L.",
    "website": "http://www.acysos.com",
    "category": "Specific Industries",
    "complexity": "normal",
    "description": """
    Communication with Epelsa Balances.
    Type Euroescale.
    Communication Socket TCP/IP.
    Protocol Ascii.
    """,
    "init_xml": [],
    'update_xml': ['data/balance_data.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
