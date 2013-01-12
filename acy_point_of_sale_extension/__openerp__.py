# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Point of sale - Extension",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "http://www.acysos.com",
    "category": "Generic Modules/Sales & Purchases",
    "description" : """Point of sale extension. Allow add negative quantities. Create picking for stock.\n""",
    "depends" : [ 
        'account',
        'point_of_sale',
        'stock',
    ], 
    "category" : "Generic Modules/Sale",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "active": False,
    "installable": True
}

