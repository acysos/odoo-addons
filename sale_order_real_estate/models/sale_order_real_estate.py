# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Iñaki Santos <isantos@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
########################################################################

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    OPERATIONS = [('sale', 'Sale'),
                  ('rent', 'Rent')]
    operation = fields.Selection(OPERATIONS, string='Operation',
                                 default='sale', required=True)

    top_id = fields.Many2one(comodel_name='real.estate.top',
                             string='Real estate top')

    @api.onchange('product_id')
    def rental_product_id_change(self):
        super(SaleOrderLine, self).rental_product_id_change()
        if self.top_id:
            self.product_uom_qty * self.price.unit


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    isrent = fields.Boolean(compute='compute_isrent', default=False,
                            store=True)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            for line in order.order_line:
                if line.top_id:
                    if line.operation:
                        if line.operation == 'sale':
                            line.top_id.operation_state = 'sold'
                        elif line.operation == 'rent':
                            line.top_id.operation_state = 'rented'
        return res

    @api.multi
    def action_confirm_key_delivery(self):
        for order in self:
            for line in order.order_line:
                if line.top_id.operation_state == 'sold':
                    line.top_id.operation_state = 'none'
                if line.top_id.operation_state == 'rented':
                    line.top_id.operation_state = 'none'
            order.isrent = False
        return True

    @api.multi
    @api.depends('order_line')
    def compute_isrent(self):
        for order in self:
            for line in order.order_line:
                if line.operation == 'rent':
                    order.isrent = True
