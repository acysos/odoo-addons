# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from osv import osv, fields
import decimal_precision as dp

import math
import re
from tools.translate import _

class product_autocontrol(osv.osv):
    _name='product.autocontrol'
    _description = 'Product Autocontrols'
    
    _columns = {
        'sequence': fields.integer('Sequence',required=True),
        'name': fields.char('Name', required=True, size=128, translate=True),
        'tolerance': fields.char('Tolerance', size=128, translate=True),
        'frecuency': fields.char('Frecuency', size=128, translate=True),
        'tools': fields.char('Tools', size=128, translate=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade'),
    }
    
    _order = 'sequence'
    
    _sql_constraints = [
        ('sequence_product_uniq', 'unique (sequence,product_id)', 'The sequence must be unique per product !')
    ]
    
product_autocontrol()

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'autocontrol_id': fields.one2many('product.autocontrol', 'product_id', 'Product Autocontrols'),
    }
    
product_product()