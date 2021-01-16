# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Account Cashdro Base",
    "version": "11.0.1.1.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Ignacio Ibeas <ignacio@acysos.com>', ],
    "category": "",
    "license": "AGPL-3",
    "description": """
    """,
    "depends": ["account"
    ],
    "external_dependencies": {
        "python": ["json",
                   "requests",
                   "webbrowser"],
    },
    "data": [
        "views/account_journal.xml",
        "views/account_bank_statement_view.xml"
    ],
    'images': ['static/description/banner.jpg'],
    "installable": True,
}
