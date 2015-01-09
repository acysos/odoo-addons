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


class purchase_order_line(osv.osv):
    '''
    Open ERP Model
    '''
    _inherit = 'purchase.order.line'

    def _get_virtual_stock(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            res[obj.id] = obj.product_id.virtual_available
        return res

    def _get_real_stock(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            res[obj.id] = obj.product_id.qty_available
        return res

    _columns = {
        'virtual_avl': fields.function(_get_virtual_stock, method=True,
                                       string='Virtual Stock'),
        'qty_avl': fields.function(_get_real_stock, method=True,
                                   string='Real Stock'),
    }
purchase_order_line()
