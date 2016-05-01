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

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp

    
class pricelist_partnerinfo(osv.osv):
    _inherit = 'pricelist.partnerinfo'
    _columns = {
        'extra_price': fields.float('Extra Price', required=True, digits_compute=dp.get_precision('Purchase Price')),
    }


class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'extra_price_purchase': fields.float('Purchase Extra Price', digits_compute=dp.get_precision('Sale Price'), help="Purchase extra price to show in the invoice like a line"),
    }
