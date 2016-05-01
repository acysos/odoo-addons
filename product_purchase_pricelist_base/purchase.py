# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2015  Acysos S.L.
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

from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    def _amount_line_with_tax(self, cr, uid, ids, prop={}, arg={},
                              context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id,
                                        line.price_subtotal, line.product_qty)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total_included'])
        return res

    def action_confirm(self, cr, uid, ids, context=None):
        super(purchase_order_line, self).action_confirm(cr, uid,
            ids, context)
        prod_obj = self.pool.get('product.product')
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        for line in self.browse(cr, uid, ids, context):
            if line.product_id.cost_method == 'standard':
                if user.company_id.purchase_price_update == 'purchase':
                    if user.company_id.sale_with_tax:
                        amounts = self._amount_line_with_tax(
                           cr, uid, ids)
                        price = (amounts[line.id] / line.product_qty) * line.product_id.uom_po_id.factor
                    else:
                        price = (line.price_subtotal / line.product_qty) * line.product_id.uom_po_id.factor
                    prod_obj.write(cr, uid, [line.product_id.id],
                                   {'purchase_price': price,
                                    'standard_price': line.price_unit},
                                   context)
        return True

