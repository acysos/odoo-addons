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

class pos_order(osv.osv):
    _inherit = "pos.order"
    
    def action_invoice(self, cr, uid, ids, context=None):

        """Create a invoice of order  """
        print "Invoice"
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []

        for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue

            if not order.partner_id:
                raise osv.except_osv(_('Error'), _('Please provide a partner for the sale.'))

            acc = order.partner_id.property_account_receivable.id
            inv = {
                'name': 'Invoice from POS: '+order.name,
                'origin': order.name,
                'account_id': acc,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.partner_id.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
            inv_ids.append(inv_id)
            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                    'pos_visible_discount': line.visible_discount,
                    'pos_sale_price': line.sale_price,
                }
                inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]

                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id = order.partner_id.id,
                                                               fposition_id=order.partner_id.property_account_position.id)['value'])
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name
                inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                    and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                inv_line_ref.create(cr, uid, inv_line, context=context)

        for i in inv_ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', i, 'invoice_open', cr)
        return inv_ids
    
pos_order()

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
    
    def onchange_sale_price(self, cr, uid, ids, price_unit, sale_price, qty, discount):
        discount = (1 - ((sale_price*(1-discount*0.01))/price_unit))*100
        res_discount = discount
        return {'value': {'notice': '', 'price_ded': price_unit - sale_price or 0.0, 'discount': res_discount, 'price_subtotal_incl': (qty * price_unit)*(1-res_discount*0.01)  }}
    
    def onchange_visible_discount(self, cr, uid, ids, discount, price, price_unit, qty, *a):
        pos_order = self.pool.get('pos.order.line')
        res_obj = self.pool.get('res.users')
        company_disc = pos_order.browse(cr,uid,ids)
        if discount:
            if not company_disc:
                comp=res_obj.browse(cr,uid,uid).company_id.company_discount or 0.0
            else:
                comp= company_disc[0] and company_disc[0].order_id.company_id and  company_disc[0].order_id.company_id.company_discount  or 0.0
            res_discount = (1 - ((price*(1-discount*0.01))/price_unit))*100
            if discount > comp :
                return {'value': {'notice': '', 'price_ded': price * discount * 0.01 or 0.0, 'price_subtotal_incl': (qty * price) -((qty * price) * discount / 100), 'sale_price': price, 'discount':res_discount}}
            else:
                return {'value': {'notice': 'Minimum Discount', 'price_ded': price * discount * 0.01 or 0.0, 'price_subtotal_incl': (qty * price) -((qty * price) * discount / 100), 'sale_price': price, 'discount':res_discount}}
        else :
            return {'value': {'notice': 'No Discount', 'price_ded': price * discount * 0.01 or 0.0, 'price_subtotal_incl': (qty * price) -((qty * price) * discount / 100), 'sale_price': price, 'discount':discount}}
    
    _columns = {
        'notice': fields.char('Discount Notice', size=128, required=False),
        'sale_price': fields.float('Sale Price', digits_compute=dp.get_precision('Point Of Sale')),
        'visible_discount': fields.float('Discount (%)', digits=(16, 2)),
    }
    
pos_order_line()