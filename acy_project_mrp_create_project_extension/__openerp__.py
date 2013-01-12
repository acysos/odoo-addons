# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
    "name" : "Procurement - Create Project",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category" : "Generic Modules/Projects & Services",
    "description": """Project MRP - Allow create project for the sale order when it doesn't exist and add the tasks for each sale order line to this project
    Sponsored by Talleres Mutilva""",
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "procurement",
        "project_mrp",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :[],
    "active": False,
    "installable": True
}