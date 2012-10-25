# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
    "name" : "PDF Labels for partner, address, product, picking, ...",
    "version" : "1.1",
    "author" : "Zikzakmedia SL, Acysos S.L.",
    "website" : "www.zikzakmedia.com, www.acysos.com",
    "license" : "GPL-3",
    "category" : "Generic Modules",
    "description": """Flexible labels for partner, address, product, picking, ...:
  * Definition of page sizes, label manufacturers and label formats
  * Flexible label formats (page size, portrait or landscape, manufacturer, rows, columns, width, height, top margin, left margin, ...)
  * Initial data for page sizes and label formats (from Avery and Apli manufacturers)
  * Wizard to print labels. The label format, the printer margins, the font type and size, the first label (row and column) to print on the first page can be set.
  * The labels are created as Mako Templates: The label body can contain:
    1) Fixed strings like 'Ref.:'
    2) Mako fields like ${object.name}
    3) Mako control sequence %%for ... %%endfor for loops
    4) ReportLab tags <b> <i> <u> <super> <sub> <font> <barCode> <greek>
    5) ReportLab tags like <blockTable>, <tr>, <td>, ...
    6) <nextFrame/> tag where you want jump to next label.
    Note: Only 1, 2, 4 contents can be mixed in the same line.
    Note: Line with 1, 2, 4 content is inserted in a <para> tag.
    For ReportLab documentation visit http://www.reportlab.com/software/documentation/
  * Report style sheets can be defined to be used in the label body
  * The labels can be printed sorted by three different fields

  Migrated to OpenERP 6.0 for Acysos S.L.
""",
    "depends" : ["base",],
    "init_xml" : [
        "report_label_data.xml",
        "label_wizard.xml", # Needed by label_data.xml (label.create() method)
        "label_data.xml",
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/ir.model.access.csv",
        "label_view.xml",
        "label_wizard.xml",
        "report_label_view.xml",
    ],
    "active": False,
    "installable": True
}
