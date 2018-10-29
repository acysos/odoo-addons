# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account payroll import base XLS",
    "version": "11.0.0.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": [
        'Alexander Ezquevo <alexander@acysos.com>',
        'Ignacio Ibeas <ignacio@acysos.com>'],
    "category": "",
    "license": "AGPL-3",
    "description": """
    """,
    "external_dependencies": {
        "python": ["xlrd", "base64"],
    },
    "depends": [
        "account", "hr",
    ],
    "data": ["views/hr_employee.xml", "views/company_view.xml",
             "views/import_xls_view.xml", "data/data.xml",
             "security/ir.model.access.csv"
    ],
    'images': ['static/description/banner.jpg'],
    "installable": True,
}
