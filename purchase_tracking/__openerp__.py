# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2014  Acysos S.L.
#
########################################################################

{
    'name' : 'Purchase Tracking',
    'version' : '1.0',
    'author' : 'Acysos S.L.',
    'category' : 'Sale',
    'description' : """
List of purchased product with its origin and picking in one screen.
    """,
    'website': 'http://www.acysos.com',
    'images' : [],
    'depends' : ['procurement', 'stock', 'purchase', 'sale'],
    'data': [
        'views/purchase_view.xml'
    ],
    'js': [
        
    ],
    'qweb' : [
        
    ],
    'css':[
        
    ],
    'demo': [
        
    ],
    'test': [
        
    ],
    'installable': True,
    'auto_install': False,
}