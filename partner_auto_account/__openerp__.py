# -*- encoding: utf-8 -*-
########################################################################
#
# Copyright (c) 2011 NaN Projectes de Programari Lliure, S.L. All Rights Reserved.
#                    http://www.NaN-tic.com
# @authors: Ignacio Ibeas <ignacio@acysos.com
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA 'AGPL + Private Use License'!
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
    'name': 'Partner Auto Account',
    'version': '1.0',
    'depends': ['base',
                'account',
                'base_partner_sequence'],
    'author': 'Acysos S.L.',
    'website': 'http://www.acysos.com',
    'category': 'Account',
    'complexity': 'normal',
    'description': '''
    Create customer and supplier account with the partner sequence number.
    
    Based in nan_account_extension (NaN Projectes de Programari Lliure, S.L.)
    
    ''',
    'init_xml': [],
    'update_xml': ['company_view.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
#    'images' : [],
#    'certificate': 'certificate',
}