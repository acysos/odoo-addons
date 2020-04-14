# -*- coding: utf-8 -*-
# © 2016 Ignacio Ibeas - Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_retention_percentage(self):
        if self.env.user.company_id:
            return self.env.user.company_id.retention_percentage
        else:
            return 0

    @api.multi
    def _get_retention_days(self):
        if self.env.user.company_id:
            return self.env.user.company_id.retention_days
        else:
            return 0

    @api.multi
    @api.depends('residual')
    def _get_retention_state(self):
        for inv in self:
            if inv.residual == inv.retention_amount:
                inv.retention_state = True
            else:
                inv.retention_state = False

    retention_percentage = fields.Float(
        string='Retention Percetage', default=_get_retention_percentage)
    retention_days = fields.Integer(
        string='Retention Date Due', default=_get_retention_days)
    retention_amount = fields.Float(
        string='Retention Amount', readonly=True,
        digits=dp.get_precision('Account'), compute='_compute_amount')
    retention_date_due = fields.Date(
        string='Retention Date Due', readonly=True)
    retention_state = fields.Boolean(
        string='Retention Payment', compute=_get_retention_state, store=True)
    with_retention = fields.Boolean(string='With retention', default=True)

    @api.multi
    def action_date_assign(self):
        super(AccountInvoice, self).action_date_assign()
        for inv in self:
            if not inv.date_invoice:
                date = datetime.now().strftime('%Y-%m-%d')
            else:
                date = inv.date_invoice.strftime('%Y-%m-%d')
            date_ref = datetime.strptime(date, '%Y-%m-%d')
            retention_date = date_ref + relativedelta(
                days=inv.retention_days)
            inv.write({'retention_date_due': retention_date})
        return True

    @api.multi
    def action_move_create(self):
        self = self.with_context(invoice=self)
        res = super(AccountInvoice, self).action_move_create()
        company = self.env.user.company_id
        move = False
        if self.with_retention and self.type in ['out_invoice', 'out_refund']:
            if company.retention_account_out:
                move = self.env['account.move.line'].search(
                    [('invoice_id', '=', self.id),
                     ('debit', '=', self.retention_amount)])
            if move:
                move.move_id.button_cancel()
                move.account_id = company.retention_account_out.id
                move.move_id.action_post()
        elif self.with_retention and self.type in ['in_invoice', 'in_refund']:
            if company.retention_account_in:
                move = self.env['account.move.line'].search(
                    [('invoice_id', '=', self.id),
                     ('credit', '=', self.retention_amount)])
            if move:
                move.move_id.button_cancel()
                move.account_id = company.retention_account_in.id
                move.move_id.action_post()
        return res

    @api.multi
    def move_line_id_payment_get(self):
        res = super(AccountInvoice, self).move_line_id_payment_get()
        if self.state == 'open':
            company = self.env.user.company_id
            if self.type in ['out_invoice', 'out_refund']:
                account_id = company.retention_account_out.id
            else:
                account_id = company.retention_account_in.id
            moves = self.env['account.move.line'].search(
                [('invoice_id', '=', self.id), ('account_id', '=', account_id)])
            if moves:
                for move in moves:
                    res.append(move.id)
        return res

    @api.one
    @api.depends(
        'move_id.line_ids.full_reconcile_id.reconciled_line_ids',
        'move_id.line_ids.matched_debit_ids.debit_move_id',
        'move_id.line_ids.matched_credit_ids.credit_move_id'
    )
    def _compute_payments(self):
        super(AccountInvoice, self)._compute_payments()
        partial_lines = lines = self.env['account.move.line']
        company = self.env.user.company_id
        for line in self.move_id.line_ids:
            if line.account_id not in [
                    company.retention_account_out,
                    company.retention_account_in]:
                continue
            if line.full_reconcile_id:
                lines |= line.full_reconcile_id.reconciled_line_ids
            elif line.matched_debit_ids:
                lines |= line.matched_debit_ids.debit_move_id
            elif line.matched_credit_ids:
                lines |= line.matched_credit_ids.credit_move_id
            partial_lines += line
        self.payment_move_line_ids = (
            lines - partial_lines + self.payment_move_line_ids).sorted()

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        if self.with_retention:
            if self.env.user.company_id.with_taxes:
                amount = self.amount_total * self.retention_percentage / 100
            else:
                amount = self.amount_untaxed * self.retention_percentage / 100
        else:
            amount = 0
        self.retention_amount = amount
