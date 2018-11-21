# -*- coding: utf-8 -*-
# Copyright (C) 2015 Therp BV (<http://therp.nl>).
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from decimal import Decimal
from openerp import models, api
from openerp.tools.float_utils import float_repr


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.model
    def get_possible_payment_orders_for_statement_line(self):
        """find orders that might be candidates for matching a statement
        line"""
        self.ensure_one()
        digits = self.env['decimal.precision'].precision_get('Account')
        order_ids = self.env['account.payment.order'].search(
            [('total_company_currency', '=', self.amount),
             ('state', '=', 'uploaded')])
        # verify that this ids are accessible to the user and from the
        # right bank account if applicable
        domain = [
            ('id', 'in', order_ids.ids),
        ]
        if self.bank_account_id.acc_number:
            domain.append(
                ('mode.bank_id.acc_number', '=',
                 self.bank_account_id.acc_number))
        return self.env['account.payment.order'].search(domain)

    @api.model
    def get_reconcile_lines_from_order(self, orders, excluded_ids=None):
        """return lines to reconcile our statement line with"""
        self.ensure_one()
        order = orders[0]
        if order.state == 'uploaded':
            move_lines_list = list(set(order._get_transfer_move_lines()))
        else:
            move_lines = order.line_ids.mapped('move_line_id').filtered(
                lambda x: not x.reconcile_id)
            move_lines_list = [x for x in move_lines]
        return self.env['account.move.line']\
            .prepare_move_lines_for_reconciliation_widget(move_lines_list)

    @api.model
    def get_reconciliation_proposition(self, excluded_ids=None):
        """See if we find a set payment order that matches our line. If yes,
        return all unreconciled lines from there"""
        self.ensure_one()
        orders = self.get_possible_payment_orders_for_statement_line()
        if orders:
            reconcile_lines = []
            for order in orders:
                for payment_line in order.payment_line_ids:
                    if payment_line.move_line_id:
                        reconcile_lines.append(payment_line.move_line_id.id)
            if reconcile_lines:
                return self.env['account.move.line'].browse(reconcile_lines)
        return super(AccountBankStatementLine, self)\
            .get_reconciliation_proposition(excluded_ids=excluded_ids)
