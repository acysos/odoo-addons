# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models, exceptions


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_number(self):
        res = super(AccountInvoice, self).action_number()
        for inv in self:
            self.env['account.invoice.line'].update_asset(inv.invoice_line)
        return res

    @api.multi
    def action_cancel(self):
        super(AccountInvoice, self).action_cancel()
        for invoice in self:
            for line in invoice.invoice_line:
                if line.asset and line.dep_history:
                    if line.dep_history.dep_line1.move_id:
                        move1 = line.dep_history.dep_line1.move_id
                        if move1.state == 'posted':
                            move1.button_cancel()
                        move1.unlink()
                    if line.dep_history.dep_line2.move_id:
                        move2 = line.dep_history.dep_line2.move_id
                        if move2.state == 'posted':
                            move2.button_cancel()
                        move2.unlink()
                    line.dep_history.dep_line1.move_check = False
                    line.dep_history.dep_line2.move_check = False
                    line.dep_history.unlink()
                    line.dep_history = None
                    line.asset.purchase_value -= line.price_subtotal
                    line.asset.times_changed_value -= 1
                    line.asset.compute_depreciation_board()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset = fields.Many2one(
        comodel_name='account.asset.asset', string='Asset')
    dep_history = fields.Many2one(
        comodel_name='account.asset.change.value.history')

    @api.multi
    def update_asset(self, lines):
        for line in lines:
            if line.asset:
                if line.asset.method_time != 'percentage':
                    line.asset.with_context(line_id=line.id).update_asset(
                        line.invoice_id.date_invoice, line.price_subtotal)
                else:
                    raise exceptions.Warning(_(
                        'Change asset with method time percentage is not'
                        ' allowed!'))
