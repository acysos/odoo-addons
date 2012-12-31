# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from osv import osv, fields
from tools.translate import _

class product_template(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
        'meters': fields.boolean('Has meters', help='Allow use meters with this product. Remerber change the meter description in descriptions'),
        'meter_description': fields.char('Meter description',size=128, translate=True, help='The bracket [last] will be replace by the last meter. The bracket [new] will be replace by the new meter'),
    }
    
    _defaults = {
        'meter_description': 'Last meter: [last] - New meter: [new]'
    }
    
product_template()