# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'internal_reference': fields.related('product_variant_ids', 'internal_reference',
                                    type='char', string='Internal Reference 2'),
        'internal_name': fields.related('product_variant_ids', 'internal_name',
                                    type='char', string='Internal Name'),
    }

class product_product(osv.osv):
    _inherit = "product.product"
            
    _columns = {
        'internal_reference': fields.char('Internal Reference 2', size=64),
        'internal_name': fields.char('Internal Name', size=128),
    }
    
    _order = 'default_code'
            
