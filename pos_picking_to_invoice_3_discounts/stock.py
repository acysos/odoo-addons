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

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, 
                              invoice_id, invoice_vals, context=None):
        res = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, 
                       picking, move_line, invoice_id, invoice_vals, context)
        if group:
            name = (picking.date or '') + '-' + (move_line.product_id.name or move_line.name)
        else:
            name = (move_line.product_id.name or move_line.name)
        res['name'] = name
        if move_line.negative:
            res['quantity'] = -abs(res['quantity'])
        if move_line.pos_line_id:
            res['price_unit'] = move_line.pos_line_id.price_unit
            res['discount1'] = move_line.pos_line_id.discount
        return res

stock_picking()