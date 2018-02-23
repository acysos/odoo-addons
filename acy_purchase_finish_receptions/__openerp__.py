# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
    "name" : "Purchase finish receptions",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "category" : "Generic Modules/Sales & Purchases",
    "website" : "www.acysos.com",
    "description": """Finish a purchase order when you don't receive more pickings
    
    """,
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "purchase",
        "decimal_precision",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :['purchase_view.xml'],
    "active": False,
    "installable": True
}