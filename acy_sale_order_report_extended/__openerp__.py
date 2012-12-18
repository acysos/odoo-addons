##############################################################################
#  
#    Copyright (C) 2004-2010 Yannick Soldati. All Rights Reserved
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
    "name" : "Sale order report extended",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "category" : "Generic Modules/Sales & Purchases",
    "website": "http://www.acysos.com",
    "description": """
    Sale order report extended
    
    With the sale order report extended module, you can:
     - configure 4 types of templates for sale orders:
         *Headers
         *Footers
         *Options
         *Special conditions
     - Select these templates when you make a sale order so they 
     appear on the sale order report and modify them if needed
     - Image support. Add image of the product like a appendix.
    
    Update by Acysos S.L from sale_order_extended for OpenERP 5.0 of PCSOL. New support for images added by Acysos S.L. and multilanguage.
    """,
    "license" : "AGPL-3",
    "depends" : ['sale', 'product_images_olbs', 'product_images_repository'],
    "init_xml" : [],
    "update_xml" : ['sale_order_report_extended_view.xml',
                    'sale_order_report_extended.xml'],
    "active": False,
    "installable": True,
}   
