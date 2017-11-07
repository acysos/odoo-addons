# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime


DFORMAT = "%Y-%m-%d"


class FeedEvent(models.Model):
    _name = 'farm.feed.event'
    _inherit = {'farm.event.feed_mixin': 'FeedEventMixin_id'}
    _auto = True

    animal_type = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),
        ('individual', 'Individual'), ('group', 'Group'),
        ], string="Animal Type", select=True)
    feed_quantity_animal_day = fields.Float(string='Qty. per Animal Day',
                                            digits=(16, 4),
                                            compute='get_feed_per_day')
    feed_inventory = fields.Many2one(comodel_name='farm.feed.inventory',
                                     string='Inventory')
    feed_inventory = fields.Selection(string='Inventory',
                                      selection='get_inventory',
                                      readonly=True, select=True,
                                      help='The inventory that generated this'
                                      'event automatically.')

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(FeedEvent, self).create(vals)
        if len(res.move) == 0:
            quants_obj = self.env['stock.quant']
            moves_obj = self.env['stock.move']
            target_quant = quants_obj.search([
                ('lot_id', '=', res.feed_lot.id),
                ('location_id', '=', res.feed_location.id)])
            new_move = moves_obj.create({
                'name': res.job_order.name+'-'+res.lot.name+'-mov',
                'create_date': fields.Date.today(),
                'date': res.start_date,
                'product_id': res.feed_product.id,
                'product_qty': res.feed_quantity,
                'product_uom': res.uom.id,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location.id,
                'company_id': res.location.company_id.id,
                'origin': res.job_order.name,
                })
            for q in target_quant:
                q.reservation_id = new_move.id
            res.move = new_move
            new_move.action_done()
        return res

    @api.multi
    def get_feed_per_day(self):
        for res in self:
            if res.animal or res.animal_group:
                if res.feed_quantity and res.start_date and res.end_date:
                    days = (datetime.strptime(res.end_date, DFORMAT) -
                            datetime.strptime(res.start_date, DFORMAT)).days
                    if days > 0:
                        qty = 1
                        res.feed_quantity_animal_day = \
                            (res.feed_quantity/res.quantity)/days

    @api.onchange('move')
    @api.multi
    def onchange_move(self):
        for res in self:
            if len(res.move) > 0:
                res.feed_product = res.move.product_id
                res.uom = res.move.product_uom
                res.feed_quantity = res.move.product_qty
                res.farm = res.move.location_dest_id.location_id.location_id
                res.feed_location = res.move.location_id
                res.location = res.move.location_dest_id
                if len(res.move.reserved_quant_ids) > 0:
                    res.feed_lot = res.move.reserved_quant_ids[0].lot_id
                else:
                    if len(res.move.quant_ids) > 0:
                        res.feed_lot = res.move.quant_ids[-1].lot_id

    

    @api.one
    def confirm(self):
        quants_obj = self.env['stock.quant']
        if self.animal_type == 'group':
            self.animal_group.feed_quantity += self.feed_quantity
            self.set_cost(
                self.animal_group.account, self.feed_lot, self.feed_quantity)
        else:
            self.animal.consumed_feed += self.feed_quantity
            self.set_cost(
                self.animal.account, self.feed_lot, self.feed_quantity)
        self.consume_feed('consume_feed', self.end_date, self.feed_product,
                          self.feed_lot, self.specie, self.location,
                          self.feed_quantity, self.uom)
        super(FeedEvent, self).confirm()

    @api.one
    def set_cost(self, account, lot, qty):
        company = self.env['res.company'].search([
            (True, '=', True)])[0]
        journal = self.env['account.analytic.journal'].search([
            ('code', '=', 'FAR')])
        analytic_line_obj = self.env['account.analytic.line']
        stock_move_obj = self.env['stock.move']
        cost = 0
        if lot.unit_cost and lot.unit_cost > 0:
            cost = lot.unit_cost * qty
        else:
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
        analytic_line_obj.create({
            'name': self.job_order.name,
            'date': self.end_date,
            'ref': 'feed',
            'amount': -(cost),
            'unit_amount': qty,
            'account_id': account.id,
            'general_account_id': company.feed_account.id,
            'journal_id': journal.id,
            })

    def get_inventory(self):
        irModel_obj = self.env['ir.model']
        models = irModel_obj.search([
            ('model', 'in', ['farm.feed.inventory',
                             'farm.feed.provisional_inventory']), ])
        return [('', '')] + [(m.model, m.name) for m in models]
