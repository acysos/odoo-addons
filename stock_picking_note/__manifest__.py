# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today Trey, Kilobytes de Soluciones <www.trey.es>
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Note',
    'summary': '''
        Module that allows you to add notes in stock picking''',
    'description': '''
        This module allows you to add an internal note in a stock picking
    ''',
    'author': 'Trey (www.trey.es), Acysos S.L.',
    'website': 'https://www.trey.es, https://www.acysos.com',
    'category': 'Stock',
    'version': '11.0.0.1.0',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_view.xml',
    ],
    'installable': True,
}
