# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

class AccountCashRegisterLine(models.Model):
    _inherit = 'account.cash.register.line'

    bank_deposit_id = fields.Many2one(
        comodel_name='bank.deposit', string='Bank Deposit',
        required=False)
    bank_deposit_move = fields.Many2one(
        comodel_name='bank.deposit.move',
        string="Bank Deposit Move")
    bank_deposit_balance = fields.Float(string='Available',
                                       related='bank_deposit_id.amount')


class AccountCashStatementRegister(models.Model):
    _inherit = 'account.cash.statement.register'

    @api.multi
    def button_confirm(self):
        super(AccountCashStatementRegister, self).button_confirm()
        for line in self.line_ids:
            if line.bank_deposit_id:
                deposit_move_model = self.env['bank.deposit.move']
                balance = line.bank_deposit_id.amount + line.amount
                if balance < 0:
                    raise except_orm(_('Warning!'), _('Try to get more money that is available!'))
                else:
                    vals = {
                        'name': '[' + line.ref or '/' + '] ' + line.name or '/',
                        'date': self.date,
                        'amount': line.amount,
                        'deposit_id': line.bank_deposit_id.id,
                        'balance': balance,
                    }
                    line.bank_deposit_id.amount = balance
                    line.bank_deposit_move = deposit_move_model.create(vals)
                
    @api.multi
    def button_cancel(self):
        super(AccountCashStatementRegister, self).button_cancel()
        for line in self.line_ids:
            line.bank_deposit_move.unlink()
