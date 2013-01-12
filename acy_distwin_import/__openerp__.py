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
    "name" : "Distwin import module",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category": "Tools",
    "description": """DEVELOPMENT VERSION. Allow import partners and invoices from the excel files exported by Distwin. Remember save the distwin excel file like csv.
    TODO: Import invoices, improve speed.
    """,
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "base_tools",
        "account",
        "nan_account_extension",
        "base_vat",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :['partner_import.xml','supplier_import.xml'],
    "active": False,
    "installable": True
}