# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "POS Payment Cashdro",
    "version": "11.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Ignacio Ibeas <ignacio@acysos.com>', ],
    "category": "",
    "license": "AGPL-3",
    "description": """
    """,
    "depends": ["point_of_sale", "account_cashdro"
    ],
    "data": [
        "views/pos_config.xml",
        "views/account_journal.xml",
        "views/assets.xml"
    ],
    'qweb': ['static/src/xml/pos_cashdro_terminal.xml'],
    'images': ['static/description/banner.jpg'],
    "installable": True,
}
