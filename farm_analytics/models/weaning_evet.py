
from odoo import models, fields, api, _

class WeaningEvent(models.Model):
    _inherit = 'farm.weaning.event'

    def confirm(self):
        for res in self:
            super(WeaningEvent, res).confirm()
            company = self.env['res.company'].search([
                (True, '=', True)])[0]
            journal = self.env['account.analytic.journal'].search([
                ('code', '=', 'FAR')])
            analytic_line_obj = self.env['account.analytic.line']
            tot_cost = 0
            for line in res.animal.account.line_ids:
                tot_cost = tot_cost + line.amount
            analytic_line_obj.create({
                'name': 'weaning Cost',
                'date': res.timestamp,
                'ref': 'farrow',
                'amount': tot_cost,
                'unit_amount': 1,
                'account_id': res.weared_group.account.id,
                'general_account_id': company.feed_account.id,
                'journal_id': journal.id,
            })
            analytic_line_obj.create({
                'name': 'weaning Cost',
                'date': res.timestamp,
                'ref': 'farrow',
                'amount': -(tot_cost),
                'unit_amount': 1,
                'account_id': res.animal.account.id,
                'general_account_id': company.feed_account.id,
                'journal_id': journal.id,
            })
