# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class MedicationEvent(models.Model):
    _name = 'farm.medication.event'
    _inherit = {'farm.event.feed_mixin': 'FeedEventMixin_id'}
    _auto = True

    medication_in_feed = fields.Boolean(string='Medication in feed',
                                        default=False)
    medicated_feed = fields.Many2one(string='Medicated Feed',
                                     comodel_name='product.product')
    feed_product_uom_category = fields.Many2one(
        comodel_name='product.uom.categ', string='Feed Uom Category',
        readonly=True)

    def confirm(self):
        for res in self:
            if not res.medication_in_feed:
                quants_obj = self.env['stock.quant']
                moves_obj = self.env['stock.move']
                target_quant = quants_obj.search([
                    ('lot_id', '=', res.feed_lot.id),
                    ('location_id', '=', res.feed_location.id)])
                medication_cost = 0
                for tq in target_quant:
                    medication_cost = tq.cost
                if len(res.move) == 0:
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
                    res.move = new_move
                    for q in target_quant:
                        q.reservation_id = new_move.id
                    new_move.action_done()
                res.consume_feed('consume_feed', res.end_date, res.feed_product,
                                  res.feed_lot, res.specie, res.location,
                                  res.feed_quantity, res.uom)
                if res.animal_type == 'group':
                    account = res.animal_group.account
                else:
                    account = res.animal.account
                res.set_cost(account, medication_cost, res.feed_quantity)
        super(MedicationEvent, self).confirm()

    def set_cost(self, account, cost, qty):
        company = self.env['res.company'].search([
            ('id', '=', self.farm.company_id.id)])
        journal = self.env['account.analytic.journal'].search([
            ('code', '=', 'FAR')])
        analytic_line_obj = self.env['account.analytic.line']
        analytic_line_obj.create({
            'name': self.job_order.name,
            'date': self.end_date,
            'amount': -(cost * qty),
            'unit_amount': qty,
            'account_id': account.id,
            'general_account_id': company.feed_account.id,
            'journal_id': journal.id,
            })
