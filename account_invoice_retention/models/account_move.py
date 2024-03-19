# -*- coding: utf-8 -*-
# © 2016 Ignacio Ibeas - Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_residual')
    def _get_retention_state(self):
        for inv in self:
            if inv.amount_residual == inv.retention_amount:
                inv.retention_state = True
            else:
                inv.retention_state = False

    retention_percentage = fields.Float(
        string='Retention Percentage')
    retention_days = fields.Integer(
        string='Retention Days')
    retention_amount = fields.Float(
        string='Retention Amount', readonly=True,
        digits=dp.get_precision('Account'), compute='_compute_amount')
    retention_date_due = fields.Date(
        string='Retention Date Due', readonly=True)
    retention_state = fields.Boolean(
        string='Retention Payment', compute=_get_retention_state, store=True)
    with_retention = fields.Boolean(string='With retention')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(AccountMove, self)._onchange_partner_id()
        if self.partner_id:
            partner = self.partner_id
            self.with_retention = partner.with_retention
            if self.with_retention:
                company = self.company_id
                retention_percentage = (
                    partner.retention_percentage or 
                    company.retention_percentage)
                retention_days = (
                    partner.retention_days or company.retention_days)
                self.retention_percentage = retention_percentage
                self.retention_days = retention_days

    def _recompute_retention_lines(self):
        self.ensure_one()
        if self.with_retention:
            existing_terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in (
                    'receivable', 'payable'))
            for line in existing_terms_lines:
                line.debit = line.debit * (1 - self.retention_percentage/100)
                line.credit = line.credit * (1 - self.retention_percentage/100)
            if existing_terms_lines:
                template_line = existing_terms_lines[0]
                invoice_date = self.invoice_date or fields.Date.today()
                retention_date_due = invoice_date + relativedelta(
                    days=self.retention_days)
                company = self.company_id
                account_id = False
                if template_line.debit != 0:
                    debit = (
                        self.amount_total * self.retention_percentage/100)
                    account_id = company.retention_account_out.id
                else:
                    debit = 0.0
                if template_line.credit != 0:
                    credit = (
                        self.amount_total * self.retention_percentage/100)
                    account_id = company.retention_account_out.id
                else:
                    credit = 0.0
                if not account_id:
                    account_id = template_line.account_id.id

                line_vals = {
                    'name': self.invoice_payment_ref or '',
                    'debit': debit,
                    'credit': credit,
                    'quantity': 1.0,
                    'date_maturity': retention_date_due,
                    'move_id': self.id,
                    'currency_id': template_line.currency_id.id,
                    'account_id': account_id,
                    'partner_id': self.commercial_partner_id.id,
                    'exclude_from_invoice_tab': True,
                    'is_retention': True,
                }
                retention_line = self.env['account.move.line'].new(line_vals)
                if not self.line_ids.filtered(lambda line: line.is_retention):
                    self.line_ids += retention_line
                self.retention_date_due = retention_date_due

    def _recompute_payment_terms_lines(self):
        super(AccountMove, self)._recompute_payment_terms_lines()
        for move in self:
            move._recompute_retention_lines()

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        for move in self:
            if move.with_retention:
                amount = move.amount_total * move.retention_percentage / 100
            else:
                amount = 0
            move.retention_amount = amount


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    is_retention = fields.Boolean(string='Is retention', default=False)

