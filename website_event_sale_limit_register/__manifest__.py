# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name' : 'Website Event Sale Limit Register',
    'version' : '1.0',
    'license': 'AGPL-3',
    'author' : 'Acysos S.L.',
    'category' : 'Website',
    'summary' : 'Limit the number of registers for each event and order',
    'website': 'http://www.acysos.com',
    'images' : [],
    'depends' : [
        'larp',
        'event',
        'website_event',
        'website_event_sale'
    ],
    'data': [
        'views/event_view.xml',
        'views/event_templates.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
