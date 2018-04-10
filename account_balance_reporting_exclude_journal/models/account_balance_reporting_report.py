# -*- coding: utf-8 -*-
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountBalanceReporting(models.Model):
    _inherit = "account.balance.reporting"

    journal_exclude = fields.Many2many(
        comodel_name='account.journal', relation='balance_report_journal',
        column1='report_id', column2='journal_id')


class AccountBalanceReportingLine(models.Model):
    _inherit = "account.balance.reporting.line"

    @api.multi
    def _calculate_value(self, domain, fyear='current'):
        if self.report_id.journal_exclude:
            journal_exclude = [(
                'journal_id', 'not in', self.report_id.journal_exclude.ids)]
            domain += journal_exclude
        value, move_lines = super(
            AccountBalanceReportingLine, self)._calculate_value(domain, fyear)
        return value, move_lines
