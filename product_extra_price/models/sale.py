# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    extra_parent_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Extra Price',
        help='The line that contain the product with the extra price')
    extra_child_line_id = fields.Many2one(comodel_name='sale.order.line',
                                          string='Line extra price', help='')

    def button_cancel(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            if not line.extra_parent_line_id and line.invoiced:
                raise Warning(_('Invalid Action!'),
                              _('You cannot cancel a sales order line'
                                ' that has already been invoiced.'))
        procurement_obj = self.pool['procurement.order']
        procurement_obj.cancel(
            cr, uid, sum([l.procurement_ids.ids for l in lines], []),
            context=context)
        return self.write(cr, uid, ids, {'state': 'cancel'})

    @api.multi
    def unlink(self):
        for res in self:
            if res.extra_child_line_id:
                res.extra_child_line_id.unlink()
            return super(sale_order_line, self).unlink()

    @api.multi
    def update_child(self, line, vals):
        if 'product_uom_qty' in vals and line.extra_child_line_id:
                line.extra_child_line_id.product_uom_qty = \
                    vals['product_uom_qty']

    @api.multi
    def write(self, vals):
        for res in self:
            self.update_child(res, vals)
            return super(sale_order_line, self).write(vals)


class sale_order(models.Model):
    _inherit = 'sale.order'

    def create(self, cr, uid, vals, context=None):
        result = super(sale_order,self).create(cr, uid, vals, context)
        self.expand_extra_prices(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(sale_order,self).write(cr, uid, ids, vals, context)
        self.expand_extra_prices(cr, uid, ids, context)
        return result
    
    def prepare_expand_extra_price_vals(self, line, order, sequence, tax_ids):
        vals = {
                    'order_id': order.id,
                    'name': '-- '+line.product_id.name_extra_price or ' ',
                    'sequence': sequence,
                    'delay': line.product_id.sale_delay or 0.0,
                    'route_id': line.route_id and line.route_id.id or False,
                    'price_unit': line.product_id.extra_price,
                    'tax_id': [(6,0,tax_ids)],
                    #'type': line.product_id.procure_method,
                    'property_ids': [(6,0,[])],
                    'address_allotment_id': False,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos_qty': line.product_uos_qty,
                    'product_uos': line.product_uos.id,
                    'product_packaging': False,
                    'move_ids': [(6,0,[])],
                    'discount': line.discount,
                    'invoiced': True,
                    'number_packages': False,
                    'notes': False,
                    'th_weight': False,
                    'state': 'draft',
                    'extra_parent_line_id': line.id,
                    'product_id': line.product_id.product_id_extra.id or None,
                }
        return vals

    def expand_extra_prices(self, cr, uid, ids, context={}):
        if type(ids) in [int, long]:
            ids = [ids]
        updated_orders = []
        for order in self.browse(cr, uid, ids, context):
            fiscal_position = order.fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, order.fiscal_position.id, context) or False
            sequence = -1
            reorder = []
            for line in order.order_line:
                sequence += 1
                if sequence > line.sequence:
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {
                        'sequence': sequence,
                    }, context)
                else:
                    sequence = line.sequence
                if line.state != 'draft':
                    continue
                if not line.product_id:
                    continue
                if line.product_id.extra_price == 0:
                    continue
                if line.extra_child_line_id:
                    continue
                sequence += 1
                tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, line.product_id.product_id_extra.taxes_id)
                vals = self.prepare_expand_extra_price_vals(
                    line, order, sequence, tax_ids)

                extra_line = self.pool.get('sale.order.line').create(cr, uid, vals, context)
                if not order.id in updated_orders:
                    updated_orders.append( order.id )

                self.pool.get('sale.order.line').write(cr,uid,[line.id],{'extra_child_line_id':extra_line})
                for id in reorder:
                    sequence += 1
                    self.pool.get('sale.order.line').write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)
        return