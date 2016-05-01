# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from openerp import exceptions
from datetime import datetime
from datetime import timedelta


class bank_deposit_rate(models.Model):
    _name = 'bank.deposit.rate'

    name = fields.Char(string='Name')
    rate = fields.Float(string='Interest Rate',
                        digits=dp.get_precision('Account'))


class bank_deposit_move(models.Model):
    _name = 'bank.deposit.move'

    name = fields.Char(string='Concept')
    date = fields.Date(string='Date', default=fields.Date.today())
    amount = fields.Float(string='Amount',
                          digits=dp.get_precision('Account'))
    deposit_id = fields.Many2one(comodel_name='bank.deposit',
                                 string='Deposit')
    balance = fields.Float(string='Balance',
                           digits=dp.get_precision('Account'))
    
    _order = 'date desc'

    @api.onchange('amount')
    def _get_balance(self):
        balance = self.deposit_id.amount + self.amount
        if balance < 0:
            raise except_orm(_('Warning!'), _('Try to get more money that is available!'))
        self.balance = balance

class bank_deposit(models.Model):
    _name = 'bank.deposit'

    name = fields.Char(string='Number')
    partner = fields.Many2one(comodel_name='res.partner', string='Partner')
    date = fields.Date(string='Open Date', default=fields.Date.today())
    last_calculate = fields.Date(string='Last Calculate', default=fields.Date.today())
    rate = fields.Many2one(comodel_name='bank.deposit.rate',
                           string='Interest Rate')
    amount = fields.Float(string='Actual Amount',
                          digits=dp.get_precision('Account'))
    move_ids = fields.One2many(comodel_name='bank.deposit.move',
                                string='Money Moves',
                                inverse_name='deposit_id')
    users = fields.Many2many(
        string='Users', comodel_name='res.users',
        relation='bank_deposit_user_rel', column1='deposit', column2='user',
        help='Users that can read to this account')
    state = fields.Selection(selection=[('open', 'Open'),
                                        ('close', 'Closed')],
                             default='open')
    
    @api.onchange('move_ids')
    def _get_amount(self):
        self.amount = 0
        for move in self.move_ids:
            self.amount += move.amount
    
    @api.model
    def _get_balance_day(self, deposit, day):
        move_model = self.env['bank.deposit.move']
        moves = move_model.search([('deposit_id', '=', deposit.id),
                                   ('date', '=', day)], order='date desc')
        
        if len(moves) > 0:
            return moves[0].balance
        else:
            return 0
        
    
    @api.multi
    def button_calculate(self):
        self.compute_interests()

    @api.multi
    def compute_interests(self):
        move_model = self.env['bank.deposit.move']
        for deposit in self:
            date = datetime.strptime(deposit.last_calculate, "%Y-%m-%d")
            end_date = datetime.strptime(fields.Date.today(), "%Y-%m-%d")
            interests = 0
            while (date < end_date):
                date += timedelta(days=1)
                day_balance = self._get_balance_day(deposit, date)
                interests += day_balance * ((deposit.rate.rate/100)/365)
            balance = deposit.amount + interests
            vals = {'name': _('[Interests]'),
                    'date': fields.Date.today(),
                    'amount': interests,
                    'deposit_id': deposit.id,
                    'balance': balance,
                    }
            move_model.create(vals)
            deposit.amount = balance
            deposit.last_calculate = fields.Date.today()
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('bank.deposit')
        return super(bank_deposit, self).create(vals)
        
