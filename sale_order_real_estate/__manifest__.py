# -*- coding: utf-8 -*-
# @author Ignacio Ibeas <ignacio@acysos.com>

{
    'name': 'Sale order real estate',
    'version': '10.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Manage sale order of estates',
    'author': 'Acysos S.L',
    'website': 'http://www.acysos.com',
    'depends': [
        'sale', 'sale_start_end_dates', 'sale_stock',
        'sales_team', 'sale_rental'],
    'data': [
        'views/sale_order_real_estate.xml',
    ],
    'demo': [],
    'installable': True,
}
