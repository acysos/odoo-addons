# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class FeedEvent(models.Model):
    _name = 'farm.feed.event'
    _inherit = {'farm.event.feed_mixin': 'FeedEventMixin_id'}
    _auto = True

    animal_type = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),
        ('individual', 'Individual'), ('group', 'Group'),
        ], string="Animal Type", select=True)
    feed_quantity_animal_day = fields.Float(string='Qty. per Animal Day',
                                            digits=(16, 4), readonly=True)
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
                'product_uom_qty': res.feed_quantity,
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
        consumed_quants = quants_obj.search([
            ('lot_id', '=', self.feed_lot.id),
            ('location_id', '=', self.location.id)])
        if not consumed_quants:
            consumed_quants = quants_obj.search([
                ('location_id', '=', self.location.id)])
        consumed_feed = self.feed_quantity
        for q in consumed_quants:
            if q.qty >= consumed_feed:
                q.qty -= consumed_feed
                consumed_feed = 0
                if q.qty == 0:
                    q.unlink()
            else:
                consumed_feed -= q.qty
                q.qty = 0
                q.unlink()
        super(FeedEvent, self).confirm()

    @api.onchange('feed_quantity')
    @api.multi
    def onchange_feed_qty(self):
        for res in self:
            if len(res.move) > 0:
                res.move.product_uom_qty = res.feed_quantity

    @api.one
    def set_cost(self, account, lot, qty):
        company = self.env['res.company'].search([
            (True, '=', True)])[0]
        journal = self.env['account.analytic.journal'].search([
            ('code', '=', 'FAR')])
        analytic_line_obj = self.env['account.analytic.line']
        if lot.unit_cost > 0:
            cost = lot.unit_cost * qty
        else:
            quants_obj = self.env['stock.quant']
            quants = quants_obj.search([
                ('lot_id', '=', self.feed_lot.id),
                ('location_id', '=', self.location.id)])
            if len(quants) < 1:
                quants = quants_obj.search([
                    ('location_id', '=', self.location.id)])
            if len(quants) < 1 or quants[0].cost == 0:
                prod_tmpl = self.feed_product.product_tmpl_id
                cost = prod_tmpl.standard_price * qty
            else:
                cost = quants[0].cost * qty
        analytic_line_obj.create({
            'name': self.job_order.name,
            'date': self.end_date,
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
