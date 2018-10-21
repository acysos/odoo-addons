# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today Trey, Kilobytes de Soluciones <www.trey.es>
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Note Purchase',
    'summary': '''
        Allows you to copy the internal note of a purchases order to the stock
        picking it generates.''',
    'description': '''
        This module allows the internal note of a purchases order to be copied
        in the delivery note that it generates.
    ''',
    'author': 'Trey (www.trey.es), Acysos S.L.',
    'website': 'https://www.trey.es, https://www.acysos.comS',
    'category': 'Purchase',
    'version': '11.0.0.1.0',
    'depends': [
        'purchase',
        'stock_picking_note',
    ]
}
