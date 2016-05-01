# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    received_rate = fields.Float(string='Received Rate',
                                compute='_get_received_rate')

    def _get_received_rate(self):
        for purchase in self:
            total_qty = 0
            total_received = 0
            for picking in purchase.picking_ids:
                if picking.state != 'cancel':
                    for move in picking.move_lines:
                        total_qty += move.product_uom_qty
                if picking.state == 'done':
                    for pack in picking.pack_operation_ids:
                        total_received += pack.product_qty
            if total_qty != 0:
                purchase.received_rate = (total_received / total_qty) * 100
