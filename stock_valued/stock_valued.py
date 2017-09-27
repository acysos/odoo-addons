# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 ACYSOS S.L. (http://acysos.com) All Rights Reserved.
#    Copyright (c) 2012 Zikzakmedia SL (http://www.zikzakmedia.com)
#    Copyright (c) 2011 NaN Projectes de Programari Lliure S.L. (http://nan-tic.com)
#    Copyright (c) 2008 ACYSOS S.L. (http://acysos.com) All Rights Reserved.
#                       Pedro Tarrafeta <pedro@acysos.com>
#    Copyright (c) 2008 Pablo Rocandio. All Rights Reserved.
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

from osv import fields, osv
import decimal_precision as dp

#----------------------------------------------------------
# Partner
#----------------------------------------------------------
class partner_new(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'alb_val': fields.boolean('Albarán valorado'), # Enviar albarán valorado
        #'parent_id': fields.many2one('res.partner','Partner', select=True), # ???
               }
    _defaults = {
        'alb_val' : lambda * a: 1,
    }
partner_new()


#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):

##For Value picking

    def _amount_untaxed(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        for picking in self.browse(cr, uid, ids, context):
            total_untaxed = 0
            for move in picking.move_lines:
                total_untaxed += move.sale_price_net * move.product_qty
            res[picking.id] = total_untaxed
        return res

    def _amount_tax(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for picking in self.browse(cr, uid, ids, context):
            res[picking.id] = picking.amount_total - picking.amount_untaxed
        return res

    def _amount_total(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for picking in self.browse(cr, uid, ids, context):
            total = 0
            for move in picking.move_lines:
                total += move.sale_price_subtotal
            res[picking.id] = total
        return res

    _name = "stock.picking"
    _description = "Picking list"
    _inherit = "stock.picking"
    _columns = {
        'amount_untaxed': fields.function(_amount_untaxed, method=True, digits_compute=dp.get_precision('Account'), string='Untaxed Amount'),
        'amount_tax': fields.function(_amount_tax, digits_compute=dp.get_precision('Account'), method=True, string='Taxes'),
        'amount_total': fields.function(_amount_total, digits_compute=dp.get_precision('Account'), method=True, string='Total'),
        'tracking': fields.char('Tracking', size=64),
            }

stock_picking()

#----------------------------------------------------------
# Stock Move
#----------------------------------------------------------
class stock_move(osv.osv):

    def _sale_prices(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context):
            if line.sale_line_id:
                cur = line.sale_line_id.order_id.pricelist_id.currency_id
                subtotal = cur_obj.round(cr, uid, cur,
                        line.sale_line_id.price_unit * line.product_qty \
                        * (1 - (line.sale_line_id.discount or 0.0) / 100.0))
                net = line.sale_line_id.price_subtotal/line.product_qty
                unit = line.sale_line_id.price_unit
                discount = line.sale_line_id.discount
                res[line.id] = {
                    'sale_price_subtotal': subtotal,
                    'sale_price_net': net,
                    'sale_price_unit': unit,
                    'sale_discount': discount,
                }
            else:
                res[line.id] = {
                    'sale_price_subtotal': 0,
                    'sale_price_net': 0,
                    'sale_price_unit': 0,
                    'sale_discount': 0,
                }
        return res

    _inherit = "stock.move"
    _columns = {
        'sale_line_id': fields.many2one('sale.order.line', 'Sale Order Line'),
        'sale_price_subtotal': fields.function(_sale_prices, method=True,
                                        digits=(16, 2), string='Subtotal',
                                        select=True, multi='sales'),
        'sale_price_net': fields.function(_sale_prices, method=True,
                                        digits=(16, 2), string='Net',
                                        select=True, multi='sales'), # Con descuento aplicado
        'sale_price_unit': fields.function(_sale_prices, method=True,
                                        digits=(16, 2), string='Price',
                                        select=True, multi='sales'),
        'sale_discount': fields.function(_sale_prices, method=True,
                                        digits=(16, 2), string='Discount (%)',
                                        select=True, multi='sales'),
               }
stock_move()

