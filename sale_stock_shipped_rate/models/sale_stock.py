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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipped_rate = fields.Float(string='Shipped Rate',
                                compute='_get_shipped_rate')

    def _get_shipped_rate(self):
        for sale in self:
            total_qty = 0
            total_shipped = 0
            for picking in sale.picking_ids:
                if picking.state != 'cancel':
                    for move in picking.move_lines:
                        total_qty += move.product_uom_qty
                if picking.state == 'done':
                    for pack in picking.pack_operation_ids:
                        total_shipped += pack.product_qty
            if total_qty != 0:
                sale.shipped_rate = (total_shipped / total_qty) * 100
