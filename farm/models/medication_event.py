# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


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

    @api.one
    def confirm(self):
        if not self.medication_in_feed:
            quants_obj = self.env['stock.quant']
            moves_obj = self.env['stock.move']
            target_quant = quants_obj.search([
                ('lot_id', '=', self.feed_lot.id),
                ('location_id', '=', self.feed_location.id)])
            medication_cost = target_quant.cost
            if len(self.move) == 0:
                new_move = moves_obj.create({
                    'name': self.job_order.name+'-'+self.lot.name+'-mov',
                    'create_date': fields.Date.today(),
                    'date': self.start_date,
                    'product_id': self.feed_product.id,
                    'product_uom_qty': self.feed_quantity,
                    'product_uom': self.uom.id,
                    'location_id': self.feed_location.id,
                    'location_dest_id': self.location.id,
                    'company_id': self.location.company_id.id,
                    'origin': self.job_order.name,
                    })
                for q in target_quant:
                    q.reservation_id = new_move.id
                new_move.action_done()
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
                self.move = new_move
            if self.animal_type == 'group':
                account = self.animal_group.account
            else:
                account = self.animal.account
            self.set_cost(account, medication_cost, self.feed_quantity)
        super(MedicationEvent, self).confirm()

    @api.multi
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
