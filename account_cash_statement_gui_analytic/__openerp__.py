# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
    'name' : 'Account Cash Statement Gui with Analytic Plans',
    'version' : '1.0',
    'author' : 'Acysos S.L.',
    'category' : 'Account',
    'description' : """
Add Analytic Plans to Cash Statement Gui
    """,
    'website': 'http://www.acysos.com',
    'images' : [],
    'depends' : ['account', 'analytic', 'account_analytic_plans',
                 'account_cash_statement_gui'],
    'data': ['views/account_cash_statement_view.xml',
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