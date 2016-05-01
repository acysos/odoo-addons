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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

from openerp.tools.translate import _

class product_autocontrol(osv.osv):
    _name='product.autocontrol'
    _description = 'Product Autocontrols'
    
    _columns = {
        'sequence': fields.integer('Sequence',required=True),
        'name': fields.char('Name', required=True, size=128, translate=False),
        'tolerance': fields.char('Tolerance', size=128, translate=False),
        'frecuency': fields.char('Frecuency', size=128, translate=False),
        'tools': fields.char('Tools', size=128, translate=False),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade'),
        'application':fields.selection([
            ('start','Start'),
            ('middle','Middle'),
            ('final','Final'),
             ],'Application'),
        'type':fields.selection([
            ('boolean','Boolean'),
            ('number','Number'),
            ('string','String'),
            ('date','Date'),
             ],'Type'),
        'res_boolean':fields.boolean('Boolean'),
        'res_min_margin': fields.float('Min. Margin', 
                     help="Use for type number and date in number of days"),
        'res_max_margin': fields.float('Max. Margin', 
                     help="Use for type number and date in number of days"),
        'res_string': fields.char('String', size=256),
    }
    
    _order = 'sequence'
    
    _defaults = {  
        'application': 'print',  
        }
    
    _sql_constraints = [
        ('sequence_product_uniq', 'unique (sequence,application,product_id)',
        'The sequence must be unique per product and application !')
    ]


class product_product(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'autocontrol_id': fields.one2many('product.autocontrol', 'product_id', 'Product Autocontrols'),
    }
    
