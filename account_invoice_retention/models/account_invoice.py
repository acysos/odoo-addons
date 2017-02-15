# -*- coding: utf-8 -*-
# © 2016 Ignacio Ibeas - Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp


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

    retention_percentage = fields.Float(string='Retention Percetage',
                                        default=_get_retention_percentage)
    retention_days = fields.Integer(string='Retention Date Due',
                                    default=_get_retention_days)
    retention_amount = fields.Float(string='Retention Amount', readonly=True,
                                    digits=dp.get_precision('Account'),
                                    compute='_compute_amount')
    retention_date_due = fields.Date(streing='Retention Date Due',
                                     readonly=True)
    retention_state = fields.Boolean(string='Retention Payment',
                                     compute=_get_retention_state, store=True)
    with_retention = fields.Boolean(string='With retention', default=True)

    @api.multi
    def action_date_assign(self):
        super(AccountInvoice, self).action_date_assign()
        for inv in self:
            if not inv.date_invoice:
                date = datetime.now().strftime('%Y-%m-%d')
            else:
                date = inv.date_invoice
            date_ref = datetime.strptime(date, '%Y-%m-%d')
            retention_date = date_ref + relativedelta(
                days=inv.retention_days)
            inv.write({'retention_date_due': retention_date})
        return True

    @api.multi
    def action_move_create(self):
        self = self.with_context(invoice=self)
        res = super(AccountInvoice, self).action_move_create()
        if self.with_retention and self.type in ['out_invoice', 'out_refund']:
            company = self.env.user.company_id
            if company.retention_account:
                move = self.env['account.move.line'].search(
                    [('invoice', '=', self.id),
                     ('debit', '=', self.retention_amount)])
                if move:
                    move.account_id = company.retention_account.id
        return res

    @api.multi
    def move_line_id_payment_get(self):
        res = super(AccountInvoice, self).move_line_id_payment_get()
        if self.state == 'open':
            account_id = self.env.user.company_id.retention_account.id
            moves = self.env['account.move.line'].search(
                [('invoice', '=', self.id), ('account_id', '=', account_id)])
            if moves:
                for move in moves:
                    res.append(move.id)
        return res

    @api.one
    @api.depends(
        'move_id.line_id.reconcile_id.line_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids',
    )
    def _compute_payments(self):
        super(AccountInvoice, self)._compute_payments()
        partial_lines = lines = self.env['account.move.line']
        for line in self.move_id.line_id:
            if line.account_id != self.env.user.company_id.retention_account:
                continue
            if line.reconcile_id:
                lines |= line.reconcile_id.line_id
            elif line.reconcile_partial_id:
                lines |= line.reconcile_partial_id.line_partial_ids
            partial_lines += line
        self.payment_ids = (lines - partial_lines + self.payment_ids).sorted()

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
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
