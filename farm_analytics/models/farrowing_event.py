# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>.
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class FarrowingEvent(models.Model):
    _inherit = 'farm.farrowing.event'

    def confirm(self):
        company = self.user.company_id
        journal = self.env['account.analytic.journal'].search([
            ('code', '=', 'FAR')])
        analytic_line_obj = self.env['account.analytic.line']
        for res in self:
            super(FarrowingEvent, res).confirm()
            tot_cost = 0
            for line in res.animal.account.line_ids:
                tot_cost = tot_cost + line.amount
            analytic_line_obj.create({
                'name': 'Farrow Cost',
                'date': res.timestamp,
                'ref': 'farrow',
                'amount': tot_cost,
                'unit_amount': 1,
                'account_id': new_group[0].account.id,
                'general_account_id': company.feed_account.id,
                'journal_id': journal.id,
            })
            analytic_line_obj.create({
                'name': 'Farrow Cost',
                'date': res.timestamp,
                'ref': 'farrow',
                'amount': -(tot_cost),
                'unit_amount': 1,
                'account_id': res.animal.account.id,
                'general_account_id': company.feed_account.id,
                'journal_id': journal.id,
            })