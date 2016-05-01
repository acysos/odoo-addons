# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Live action role-playing game',
    'version' : '1.0',
    'license': 'AGPL-3',
    'author' : 'Acysos S.L.',
    'category' : 'Specific',
    'summary' : 'LARP organization',
    'website': 'http://www.acysos.com',
    'images' : [],
    'depends' : ['base', 'event', 'web_ckeditor4'],
    'data': ['security/larp_security.xml',
             'security/ir.model.access.csv',
             'views/larp_menu.xml',
             'views/larp_plot_view.xml',
             'views/larp_player_view.xml',
             'views/event_view.xml'
            ],
    'installable': True,
}