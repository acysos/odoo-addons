# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Web Hidden Fields',
    'version': '10.0.0.1.0',
    'category': 'Web',
    'author': 'Acysos S.L.',
    'website': 'www.acysos.com',
    'license': 'AGPL-3',
    'depends': [
         'base',
        ],
    'init_xml': [],
    'demo_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'views/hidden_template_view.xml'
    ],
    'active': False,
    'installable': True
}
