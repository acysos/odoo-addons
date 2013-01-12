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
    "name" : "Work Order",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category": "Generic Modules/Sales & Purchases",
    "description": """Make a work order.\n
        The work order is a window, that allow to administrate several order and their projects.
    Sponsored by Talleres Mutilva""",
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "sale",
        "project",
        "acy_project_with_tasks",
        "account",
        "acy_project_mrp_create_project_extension"
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :["workorder.xml", "workorder_sequence.xml","security/ir.model.access.csv","invoice.xml","project.xml","sale.xml"],
    "active": False,
    "installable": True
}