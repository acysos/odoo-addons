# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
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

"""Inherit stock_picking to add early payment discount from purchase order"""

from osv import osv

class stock_picking(osv.osv):
    """Inherit stock_picking to add early payment discount from purchase order"""

    _inherit = "stock.picking"

    def _invoice_hook(self, cursor, user, picking, invoice_id):
        '''Call after the creation of the invoice from picking, add early payment discount from purchase order'''
        #checks if early payment discount is defined in purchase order
        if picking and picking.purchase_id and picking.purchase_id.early_payment_discount and invoice_id:
            self.pool.get('account.invoice').write(cursor, user, [invoice_id], {'early_payment_discount': picking.purchase_id.early_payment_discount})

        return super(stock_picking, self)._invoice_hook(cursor, user, picking, invoice_id)

stock_picking()
