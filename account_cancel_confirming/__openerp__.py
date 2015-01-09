# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2014  Acysos S.L.
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
    'name': 'Account Invoice Confirming Cancel',
    'version': '1.0',
    'author': 'Acysos S.L.',
    'category': 'Accounting',
    'description': """
Cancel button for confirming view
    """,
    'website': 'http://www.acysos.com',
    'images': [],
    'depends': ['base', 'account_invoice_confirming', 'account_cancel'],
    'data': ['account_invoice_view.xml'],
    'js': [],
    'qweb': [],
    'css': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
