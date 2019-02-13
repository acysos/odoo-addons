# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def reconcile_partial(
            self, type='auto', writeoff_acc_id=False, writeoff_period_id=False,
            writeoff_journal_id=False):
        res = super(AccountMoveLine, self).reconcile_partial(
            type=type, writeoff_acc_id=writeoff_acc_id,
            writeoff_period_id=writeoff_period_id,
            writeoff_journal_id=writeoff_journal_id)
        for move in self:
            if move.invoice:
                if move.invoice.registration_key and \
                        move.invoice.registration_key.code == '07':
                    move.invoice.send_recc_payment(move)
        return res
