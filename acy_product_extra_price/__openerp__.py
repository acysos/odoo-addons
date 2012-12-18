# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
    "name" : "Product Extra Price",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category": 'Generic Modules/Inventory Control',
    "description": """Allow to add a second price to the product. This is usefull for company that have a extra variable price and need to show it in the invoice.
    
    Example of a invoice line:
        Description         Quantity        Unit Price      Subtotal
        Product Name               2           50,00 €      100,00 €
            Extra Price              2            2,53 €        5,06 €
                                                Total Invoice   105,06 €
    
    Sponsored by Gatakka and Polux""",
    "license" : "AGPL-3",
    "depends" : ["base", "product", "sale", "decimal_precision","account"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :["product.xml"],
    "active": False,
    "installable": True
}