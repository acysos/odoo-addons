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
    "name" : "Product Meter",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "category" : "Generic Modules/Inventory Control",
    "website" : "www.acysos.com",
    "description": """Add a product that have meter and his quantity is calcuated from this meter. Example: electricity, aqua, gas ...""",
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "account",
        "decimal_precision",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :['product_meter_data.xml','product_meter_view.xml','product_view.xml','product_meter_sequence.xml','product_meter_workflow.xml','security/product_security.xml','security/ir.model.access.csv'],
    "active": False,
    "installable": True
}