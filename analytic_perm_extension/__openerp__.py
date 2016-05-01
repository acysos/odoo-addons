# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

{
    'name' : 'Account Analytic Permission Extension',
    'version' : '1.0',
    'author' : 'Acysos S.L.',
    'category' : 'Accounting',
    'description' : """
Add multiple user permission. User only view the account line, that is user.
    """,
    'website': 'http://www.acysos.com',
    'depends' : ['analytic'],
    'data': [
        'views/analytic_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}