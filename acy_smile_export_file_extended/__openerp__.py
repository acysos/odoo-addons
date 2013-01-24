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
    "name" : "Smile Export File Extended",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category": "Tools",
    "description": """Module that extends Smile Export File.
    
    - Support Line Counter
    - Ascii Fill Char
    - Null delimter char
    - Add domain and method filter support in underlying object""",
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "smile_export",
        "smile_export_file"
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :['export_file_view.xml'],
    "active": False,
    "installable": True
}
