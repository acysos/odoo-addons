# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class FeedEventMixin(models.Model):
    _name = 'farm.event.feed_mixin'
    _inherit = {'farm.event': 'AbstractEvent_id'}
    _auto = False

    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'internal')],
                               required=True)
    quantity = fields.Integer(string='Num. of animals', compute='get_quantity',
                              store=True)
    feed_location = fields.Many2one(comodel_name='stock.location',
                                    string='Feed Source', required=True,
                                    domain=[('usage', '=', 'internal'), ])
    feed_product = fields.Many2one(comodel_name='product.product',
                                   string='Feed')
    feed_lot = fields.Many2one(comodel_name='stock.lot',
                               string='Feed Lot', required=True)
    uom = fields.Many2one(comodel_name='uom.uom', string='UOM',
                          required=True)
    feed_quantity = fields.Float(string='Comsumed Cuantity', required=True,
                                 digits=(4, 2), default=1)
    start_date = fields.Date(string='Start Date',
                             default=fields.Date.today(),
                             help='Start date of the period in'
                             'which the given quantity of product was'
                             'consumed.')
    end_date = fields.Date(string='End Date', default=fields.Date.today(),
                           help='End date of the period in which the given'
                           'quantity of product was consumed. It is the date'
                           'of event\'s timestamp.')
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move')

    @api.onchange('feed_product')
    def onchange_feed(self):
        if self.feed_product:
            self.uom = self.feed_product.product_tmpl_id.uom_id
        else:
            self.uom = False

    @api.onchange('animal')
    def onchange_animal(self):
        if self.animal:
            self.location = self.animal.location
        else:
            self.location = False

    @api.onchange('animal_group')
    def onchange_group(self):
        if self.animal_group:
            self.location = self.animal_group.location
        else:
            self.location = False

    @api.depends('animal_type', 'animal_group')
    def get_quantity(self):
        for res in self:
            if res.animal_type == 'group':
                res.quantity = res.animal_group.quantity
            else:
                res.quantity = 1

    def get_unit_cost(self):
        cost = 0.0
        quants_obj = self.env['stock.quant']
        quants = quants_obj.search([
            ('lot_id', '=', self.feed_lot.id)])
        ids = []
        for q in quants:
            ids.append(q.id)
        moves = stock_move_obj.search([
            ('quant_ids', 'in', ids),
            ('picking_id', '!=', False)])
        amount = 0.0
        raw_qty = 0
        if len(moves) != 0:
            for move in moves:
                if move.price_unit > 0:
                    amount += move.price_unit * move.product_qty
                    raw_qty += move.product_qty
            if raw_qty > 0:
                unit_price = amount/raw_qty
                cost += qty * unit_price
        if cost == 0:
            prod_tmpl = self.feed_product.product_tmpl_id
            cost = prod_tmpl.standard_price * qty
        return cost

    def consume_feed(self, name, end_date, product, lot, specie, origin,
                     qty, uom):
        moves_obj = self.env['stock.move']
        m_line_obj = self.env['stock.move.line']
        new_move = moves_obj.create({
                'name': name,
                'create_date': fields.Date.today(),
                'date': end_date,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': uom.id,
                'location_id': origin.id,
                'location_dest_id': specie.consumed_feed_location.id,
                'company_id': origin.company_id.id,
                'picked': True,
                })
        m_line_obj.create({
            'move_id': new_move.id,
            'product_id': product.id,
            'product_uom_id': uom.id,
            'quantity': qty,
            'location_id': origin.id,
            'location_dest_id': specie.consumed_feed_location.id,
            'lot_id': lot.id,
            'company_id': origin.company_id.id,
            })
        new_move._action_done()
