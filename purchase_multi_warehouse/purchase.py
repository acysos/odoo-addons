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

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _warehouse_get(self, cr, uid, context=None):
        """ To get  Warehouse  for this order
        @return: Warehouse id """
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        if user.warehouse_id:
            print 'ID'
            warehouse_id = user.warehouse_id.id
        elif user.warehouse_ids:
            print 'IDS'
            warehouse_id = user.warehouse_ids[0].id
        else:
            print 'Other'
            res = self.pool.get('stock.warehouse').search(cr, uid, [])
            warehouse_id = res and res[0] or False
        return warehouse_id

    _defaults = {
            'warehouse_id': _warehouse_get,
        }
    
purchase_order()