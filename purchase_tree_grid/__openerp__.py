# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2014 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
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
    "name" : "Purchase Order Editable Tree Grid",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "category": "Generic Modules/Sales & Purchases",
    "depends" : ["base","purchase"],
    "init_xml" : [],
    "description": """
        Editable tree view with virtual and real stocks for purchase orders. Based in ting_sales_tree_grid.
    """,
    'update_xml': ["purchase_view.xml"],
    'installable': True,
    'active': False,

}