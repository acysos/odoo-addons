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
from openerp import exceptions

class account_cash_register_line_concept(models.Model):
    _name = 'account.cash.register.line.concept'

    name = fields.Char(string='Concept', required=True)
    account_id = fields.Many2one(comodel_name='account.account',
                                 string='Account', required=True)

class account_cash_register_line(models.Model):
    _name = 'account.cash.register.line'

    name = fields.Char(string='Communication')
    amount = fields.Float(string='Amount',
                          digits_compute=dp.get_precision('Account'))
    ref = fields.Char(string='Reference')
    concept = fields.Many2one(comodel_name='account.cash.register.line.concept',
                              string='Concept')
    cash_id = fields.Many2one(comodel_name='account.cash.statement.register',
                              string="Register")
    bank_statement_line = fields.Many2one(
        comodel_name='account.bank.statement.line',
        string="Bank Statement Line")


class account_cash_statement_register(models.Model):
    _name = 'account.cash.statement.register'

    @api.multi
    def _get_open_cash(self):
        statement = self.env['account.bank.statement'].search(
            [('state', '=', 'open'), ('user_id', '=', self.env.user.id)])
        if len(statement) > 0:
            return statement[0]
        else:
            return statement

    name = fields.Char(string='Name', required=True, copy=False,
                       readonly=True, states={'draft': [('readonly', False)]},
                       select=True)
    session = fields.Many2one(string='Cash Statement',
                              comodel_name='account.bank.statement',
                              domain=[('state', '=', 'open')], required=True,
                              default=_get_open_cash)
    line_ids = fields.One2many(string="Registers",
                               comodel_name='account.cash.register.line',
                               inverse_name='cash_id')
    date = fields.Date(string='Date', default=fields.Date.today())
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('close', 'Closed')],
                             default='draft')

    _order = 'date'

    @api.multi
    def button_confirm(self):
        if not self.line_ids:
            raise exceptions.Warning(
                _("Cannot confirm a Cash register without line"))
        if self.session.state != 'open':
            raise exceptions.Warning(
                _("Cannot confirm a Cash register with a not open statement"))
        line_model = self.env['account.bank.statement.line']
        for line in self.line_ids:
            values = {'name': line.name,
                      'date': self.date,
                      'amount': line.amount,
                      'partner_id': self.partner_id.id,
                      'account_id': line.concept.account_id.id,
                      'statement_id': self.session.id,
                      'ref': line.ref,
                      }
            line_model = self.env['account.bank.statement.line']
            line_id = line_model.create(values)
            line.bank_statement_line = line_id
        self.state = 'close'

    @api.multi
    def button_cancel(self):
        if self.session.state != 'open':
            raise exceptions.Warning(
                _("Cannot cancel a Cash register with a not "
                  "confirmed statement"))
        for line in self.line_ids:
            line.bank_statement_line.unlink()
        self.state = 'draft'
