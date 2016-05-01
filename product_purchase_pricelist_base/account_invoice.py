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


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def _amount_line_with_tax(self, cr, uid, ids, prop={}, unknow_none={}, unknow_dict={}):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        local_context = {}
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            local_context['tax_calculation_rounding_method'] = (
                    line.invoice_id.tax_calculation_rounding_method)
            taxes = tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id, price, line.quantity,
                product=line.product_id,
                address_id=line.invoice_id.address_invoice_id,
                partner=line.invoice_id.partner_id,
                context=local_context)
            print taxes
            res[line.id] = taxes['total_included']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def action_purchase_price_update(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        line_obj = self.pool.get('account.invoice.line')
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.type == 'in_invoice':
                for line in invoice.invoice_line:
                    if line.product_id.cost_method == 'standard':
                        if user.company_id.purchase_price_update == 'invoice':
                            if line.quantity != 0:
                                if user.company_id.sale_with_tax:
                                    amounts = line_obj._amount_line_with_tax(
                                       cr, uid, [line.id])
                                    price = (amounts[line.id] / line.quantity) * line.product_id.uom_po_id.factor
                                else:
                                    price = (line.price_subtotal / line.quantity) * line.product_id.uom_po_id.factor
                                prod_obj.write(cr, uid, [line.product_id.id],
                                               {'purchase_price': price,
                                                'standard_price': line.price_unit},
                                               context)
        return True

