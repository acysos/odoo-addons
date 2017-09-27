# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

from osv import osv
from osv import fields
import decimal_precision as dp
from tools.translate import _
import time

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    def action_confirm(self, cr, uid, ids, context=None):
        res = super(purchase_order_line, self).action_confirm(cr, uid,
            ids, context)
        prod_obj = self.pool.get('product.product')
        for line in self.browse(cr,uid,ids,context):
            if line.product_id.cost_method == 'standard':
                cost = line.price_subtotal/line.product_qty
                prod_obj.write(cr,uid,line.product_id.id,{'standard_price':cost},context)
        return True
    
purchase_order_line()