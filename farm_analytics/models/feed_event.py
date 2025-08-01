# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class FeedEvent(models.Model):
    _inherit = 'farm.feed.event'

    def confirm(self):
        for rec in self:
            rec.set_analytics()
        return super(FeedEvent, self).confirm()

    def set_analytics(self):
        for res in self:
            if res.animal_type == 'group':
                res.set_cost(
                    res.animal_group.account, res.feed_lot, res.feed_quantity)
            else:
                res.set_cost(
                    res.animal.account, res.feed_lot, res.feed_quantity)

    def set_cost(self, account, lot, qty):
        for res in self:
            company = self.env.user.company_id
            journal = self.env['account.analytic.journal'].search([
                ('code', '=', 'FAR')])
            analytic_line_obj = self.env['account.analytic.line']
            stock_move_obj = self.env['stock.move']
            cost = res.get_unit_cost()
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