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
    "name" : "Magento Connect Check Vat",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category" : "Generic Modules",
    "description": """Check the Vat Number and assing the correct fiscal position.
    
    If the Vat Number is European Vat Number check if it is valid with Vies Webservice.
    
    Fiscal position configuratión in Shop Configuration.
    
    This module need python vatnumber (http://code.google.com/p/vatnumber/).
    """,
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "base_vat",
        "account",
        "magento_connect"
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :["sale_view.xml"],
    "active": False,
    "installable": True
}