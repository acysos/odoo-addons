##############################################################################
#
# Copyright (c) 2010 Javier Duran <javieredm@gmail.com> All Rights Reserved.
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Updated to OpenERP 6.0
#                       Ignacio Ibeas <ignacio@acysos.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
	"name" : "Purchase extension to search or filter by supplier the products in the purchase order lines",
	"version" : "0.2",
	"author" : "Acysos S.L., Javier Duran",
    "website" : "www.acysos.com",
	"depends" : ["product", "purchase"],
	"description": """ Allow to limit available selection of Products in a Purchase Order only to those products that are supplied by selected Supplier.
	""",
	"website" : "",
    'category': 'Generic Modules/Sales & Purchases',
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["product_view.xml"],
	"active": False,
	"installable": True
}
