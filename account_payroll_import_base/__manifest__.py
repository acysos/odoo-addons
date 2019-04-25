# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account payroll import base',
    'version': '12.0.1.0',
    'author': 'Acysos S.L.',
    'website': 'www.acysos.com',
    'contributors': [
        'Alexander Ezquevo <alexander@acysos.com>',
        'Ignacio Ibeas <ignacio@acysos.com>'],
    'category': '',
    'license': 'AGPL-3',
    'depends': [
        'account', 'hr', 'base_import_file', 'account_payment_partner'
    ],
    'data': ['views/hr_employee.xml',
             'views/company_view.xml',
             'views/import_file_view.xml',
             'data/data.xml',
             'views/account_move_view.xml',
             'security/ir.model.access.csv'
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
