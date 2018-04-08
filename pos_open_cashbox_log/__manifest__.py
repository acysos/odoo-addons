# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Pos Open Cashbox Log",
    'category': 'Point of sale',
    'version': '1.0',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_view.xml',
    ],
    "installable": True,
    'author': "Acysos S.L.",
    'website': "www.acysos.com",
}
