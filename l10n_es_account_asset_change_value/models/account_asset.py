# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp import api, fields, models, exceptions


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    times_changed_value = fields.Integer(string="Times change value",
                                         default=0, copy=False)
    change_value_history = fields.One2many(
        comodel_name='account.asset.change.value.history',
        inverse_name='asset', string="Change value history")

    @api.model
    def _compute_board_undone_dotation_nb(
            self, asset, depreciation_date, total_days):
        res = super(AccountAssetAsset, self)._compute_board_undone_dotation_nb(
            asset, depreciation_date, total_days)
        if asset.times_changed_value > 0:
            res += asset.times_changed_value
        return res

    @api.multi
    def update_asset(self, date, amount, history_check=False):
        self.ensure_one()
        if amount < 0:
            raise exceptions.Warning(_(
                'You can\'t decrease the value. If the asset has minor value,'
                ' you have to make a manual depreciation!'))
        change_obj = self.env['account.asset.change.value.history']
        history_after = change_obj.search(
            [('name', '>', date), ('asset', '=', self.id)])
        if history_after and not history_check:
            for history_line in history_after:
                history_line.dep_line1.move_id.unlink()
                history_line.dep_line1.unlink()
                self.purchase_value -= history_line.amount
        if self.prorata:
            posted_depreciation_line_ids = self.depreciation_line_ids.filtered(
                lambda x: x.move_check).sorted(
                    key=lambda l: l.depreciation_date)
            unposted_depreciation_line_ids = \
                self.depreciation_line_ids.filtered(
                    lambda x: not x.move_check and x.period_line)
            first_unpost_line = unposted_depreciation_line_ids[0]
            last_period_line = self.depreciation_line_ids.filtered(
                lambda x: x.move_check and x.period_line).sorted(
                    key=lambda l: l.depreciation_date)[-1]
            if posted_depreciation_line_ids and posted_depreciation_line_ids[
                    -1].depreciation_date:
                depreciation_date = datetime.strptime(
                    posted_depreciation_line_ids[
                        -1].depreciation_date, DF).date()
            else:
                depreciation_date = datetime.strptime(
                    self._get_last_depreciation_date()[self.id], DF).date()
            change_date = datetime.strptime(date, DF).date()
            next_depreciation_date = datetime.strptime(
                    first_unpost_line.depreciation_date, DF).date()
            total_days = (next_depreciation_date - depreciation_date).days
            delta = change_date - depreciation_date
            line_amount = first_unpost_line.amount * delta.days / total_days
            residual_amount = self.value_residual - line_amount + amount
            sequence = first_unpost_line.sequence + 1
            vals1 = {
                 'amount': line_amount,
                 'asset_id': self.id,
                 'sequence': sequence,
                 'name': str(self.id) + '/' + str(sequence),
                 'remaining_value': residual_amount,
                 'depreciated_value':
                 self.purchase_value - self.salvage_value - residual_amount,
                 'depreciation_date': change_date.strftime('%Y-%m-%d'),
            }
            dep_line1 = first_unpost_line.create(vals1)
            dep_line1.create_move()
            self.purchase_value += amount
            undone_dotation_number = self._compute_board_undone_dotation_nb(
                self, depreciation_date, total_days)
            if len(posted_depreciation_line_ids) == undone_dotation_number - 1:
                line_amount2 = first_unpost_line.amount - line_amount + amount
            else:
                if self.method == 'linear':
                    num_periods = len(
                            unposted_depreciation_line_ids) - 1
                    amount_period = self.value_residual / num_periods
                elif self.method == 'degressive':
                    amount_period = residual_amount * \
                        self.method_progress_factor
                change_lines = self.depreciation_line_ids.filtered(
                    lambda x: x.move_check and
                    x.depreciation_date >= last_period_line.depreciation_date
                    and not x.period_line).sorted(
                        key=lambda l: l.depreciation_date)
                amount_dep = sum(change_lines.mapped('amount'))
                line_amount2 = amount_period - amount_dep
            for line in unposted_depreciation_line_ids:
                if line == first_unpost_line:
                    amount_line = line_amount2
                    amount_residual = residual_amount - amount_line
                elif line != unposted_depreciation_line_ids[-1]:
                    amount_line = amount_period
                    amount_residual -= amount_line
                else:
                    amount_line = amount_residual
                    amount_residual = 0
                sequence += 1
                line.amount = amount_line
                line.sequence = sequence
                line.name = str(self.id) + '/' + str(line.sequence+1)
                line.remaining_value = amount_residual
                line.depreciated_value = (
                    self.purchase_value - self.salvage_value) - (
                        amount_residual + line.amount)
            self.times_changed_value += 1
        else:
            self.purchase_value += amount
        history_vals = {
            'name': date,
            'amount': amount,
            'asset': self.id,
            'dep_line1': dep_line1.id,
            'dep_line2': first_unpost_line.id
        }
        invoice_line = self.env.context.get('line_id', False)
        if invoice_line:
            history_vals['invoice_line'] = invoice_line
        history = change_obj.create(history_vals)
        if history.invoice_line:
            history.invoice_line.dep_history = history.id
        if history_after and not history_check:
            for history_line in history_after:
                self.update_asset(history_line.name, history_line.amount, True)
        return True


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'
    _order = 'sequence ASC'


class AccountAssetChangeValueHistory(models.Model):
    _name = 'account.asset.change.value.history'

    create_date = fields.Datetime(string='Create Date')
    name = fields.Date(string='Change Date')
    amount = fields.Float(string='Amount')
    user_id = fields.Many2one(comodel_name='res.users', string='User',
                              default=lambda self: self.env.user)
    invoice_line = fields.Many2one(comodel_name='account.invoice.line',
                                   string='Origin line invoice')
    asset = fields.Many2one(comodel_name='account.asset.asset',
                            string='Asset')
    dep_line1 = fields.Many2one(comodel_name='account.asset.depreciation.line',
                                string="Depreciation line change")
    dep_line2 = fields.Many2one(comodel_name='account.asset.depreciation.line',
                               string="Depreciation line period")
