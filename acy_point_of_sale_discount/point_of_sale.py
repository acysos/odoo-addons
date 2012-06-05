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
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

import netsvc
from osv import fields, osv
from tools.translate import _
from decimal import Decimal
import decimal_precision as dp


class pos_order_line(osv.osv):
    _inherit = "pos.order.line"
    
    def onchange_product_id(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False):
        price = self.price_by_product(cr, uid, ids, pricelist, product_id, qty, partner_id)
        self.write(cr, uid, ids, {'price_unit':price})
        pos_stot = (price * qty)
        return {'value': {'price_unit': price, 'sale_price': price, 'price_subtotal_incl': pos_stot}}
    
    def onchange_discount(self, cr, uid, ids, discount, price, qty, *a):
        pos_order = self.pool.get('pos.order.line')
        res_obj = self.pool.get('res.users')
        company_disc = pos_order.browse(cr,uid,ids)
        if discount:
            if not company_disc:
                comp=res_obj.browse(cr,uid,uid).company_id.company_discount or 0.0
            else:
                comp= company_disc[0] and company_disc[0].order_id.company_id and  company_disc[0].order_id.company_id.company_discount  or 0.0

            if discount > comp :
                return {'value': {'notice': '', 'price_ded': price * discount * 0.01 or 0.0, 'price_subtotal_incl': (qty * price) -((qty * price) * discount / 100), 'sale_price': price}}
            else:
                return {'value': {'notice': 'Minimum Discount', 'price_ded': price * discount * 0.01 or 0.0, 'price_subtotal_incl': (qty * price) -((qty * price) * discount / 100), 'sale_price': price}}
        else :
            return {'value': {'notice': 'No Discount', 'price_ded': price * discount * 0.01 or 0.0, 'price_subtotal_incl': (qty * price) -((qty * price) * discount / 100), 'sale_price': price}}
    
    def onchange_sale_price(self, cr, uid, ids, price_unit, sale_price, qty):
        return {'value': {'notice': '', 'price_ded': price_unit - sale_price or 0.0, 'discount': (1 - (sale_price/price_unit))*100, 'price_subtotal_incl': qty * sale_price  }}
    
    _columns = {
        'notice': fields.char('Discount Notice', size=128, required=False),
        'sale_price': fields.float('Sale Price', digits_compute=dp.get_precision('Point Of Sale')),
    }
    
pos_order_line()