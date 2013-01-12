# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Based in internetdomain module.
#                       Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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
    "name" : "Manage magazine subscriptions by number",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category": "Tools",
    "description": """Magazine subscriptions by number. Based in InternetDomain of Zikzakmedia S.L.
    Sponsored by Innovation Media Consulting.""",
    "license" : "AGPL-3",
    "depends" : [
        "base",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :["company_view.xml","magazine_view.xml","wizard/make_invoice_view.xml","security/magazine_security.xml","security/ir.model.access.csv",],
    "active": False,
    "installable": True
}