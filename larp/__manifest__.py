# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name' : 'Live action role-playing game',
    'version' : '1.0',
    'license': 'AGPL-3',
    'author' : 'Acysos S.L.',
    'category' : 'Specific',
    'summary' : 'LARP organization',
    'website': 'http://www.acysos.com',
    'images' : [],
    'depends' : ['base', 'event', 'event_sale'],
    'data': ['security/larp_security.xml',
             'security/ir.model.access.csv',
             'views/larp_menu.xml',
             'views/larp_plot_view.xml',
             'views/larp_character_view.xml',
             'views/event_view.xml'
            ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
