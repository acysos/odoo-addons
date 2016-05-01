# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
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

from openerp import models, fields, api
from openerp.tools.translate import _

class PurchaseTracking(models.Model):
    _name = 'purchase.tracking'

    @api.one
    def _total_pending(self):
        moves = self.env['stock.move'].search(
            [('purchase_line_id','=',self.purchase_line_id.id),
            ('state','=','done')])
        self.total_pend_qty = self.purchase_product_qty - \
        sum(move.product_uom_qty for move in moves)
        
    @api.one
    def _get_lots(self):
        moves = self.env['stock.move'].search(
            [('purchase_line_id','=',self.purchase_line_id.id),
            ('state','=','done')])
        lots = ''
        for move in moves:
            for lot in move.lot_ids:
                lots += lot.name + ' / '
        self.prod_lots = lots
        
    @api.one
    def _get_dates_recv(self):
        moves = self.env['stock.move'].search(
            [('purchase_line_id','=',self.purchase_line_id.id),
            ('state','=','done')])
        dates = ''
        for move in moves:
            dates += str(move.date) + ' / '
        self.dates_recv = dates
    
    name = fields.Char(default='/')
    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line', string="Purchase Line")
    purchase_date_order = fields.Datetime(
        string='Date order', related='purchase_line_id.date_order')
    purchase_order_id = fields.Many2one(string='Purchase order',
                                     related='purchase_line_id.order_id')
    purchase_product_id = fields.Many2one(
        string='Purchase product', related='purchase_line_id.product_id')
    purchase_product_name = fields.Text(
        string='Purchase Description', related='purchase_line_id.name')
    purchase_product_qty = fields.Float(string='Quantity',
                                        related='purchase_line_id.product_qty')
    purchase_product_price = fields.Float(
        string='Price Unit', related='purchase_line_id.price_unit')
    purchase_product_disc = fields.Float(
        string='Disc.', related='purchase_line_id.discount')
    purchase_product_subtotal = fields.Float(
        string='Subtotal', related='purchase_line_id.price_subtotal')
    purchase_supplier = fields.Many2one(
        string='Supplier', related='purchase_line_id.order_id.partner_id')
    purchase_date_planned = fields.Date(
        string='Date planned',
        related='purchase_line_id.order_id.minimum_planned_date')
    purchase_product_state = fields.Selection(
        string='State', related='purchase_line_id.state')
    sale_line_id = fields.Many2one(comodel_name='sale.order.line',
                                         string="Sale Line")
    sale_order_id = fields.Many2one(string='Sale Order',
                                    related='sale_line_id.order_id')
    sale_product_id = fields.Many2one(string='Sale product',
                                     related='sale_line_id.product_id')
    total_pend_qty = fields.Float(string='Qty Pending',
                                  compute='_total_pending')
    prod_lots = fields.Char(string="Lots", compute='_get_lots')
    dates_recv = fields.Char(string='Dates Recv', compute='_get_dates_recv')
    
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
     
    def create(self, cr, uid, vals, context=None):
        res_id = super(purchase_order_line, self).create(cr, uid, vals, context)
        order_line = self.browse(cr, uid, res_id, context)
        if 'scheduler' not in context:
            purchase_track_obj = self.pool.get('purchase.tracking')
            track_ids = purchase_track_obj.search(cr, uid, [('purchase_line_id','=',res_id)])
            if len(track_ids) == 0:
                vals = {
                    'purchase_line_id': res_id,
                }
                purchase_track_obj.create(cr, uid, vals, context)
         
        return res_id
    