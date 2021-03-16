# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        res = super(AccountMoveLine, self).reconcile(
            writeoff_acc_id=False, writeoff_journal_id=False)
        for move in self:
            if move.move_id.type in [
                    'out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                if move.move_id.registration_key and \
                        move.move_id.registration_key.code == '07':
                    move.move_id.send_recc_payment(move)
        return res
