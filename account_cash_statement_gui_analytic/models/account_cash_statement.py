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


# class account_cash_register_line(models.Model):
#     _inherit = 'account.cash.register.line'
# 
#     analytic_plan_id = fields.Many2one(
#        comodel_name='account.analytic.plan.instance', string='Analytic Plan')

class AccountCashRegisterLineConcept(models.Model):
    _inherit = 'account.cash.register.line.concept'

    analytic_plan_id = fields.Many2one(
        comodel_name='account.analytic.plan.instance', string='Analytic Plan',
        required=True)    
    

class AccountCashStatementRegister(models.Model):
    _inherit = 'account.cash.statement.register'

    analytic_plan_id = fields.Many2one(
       comodel_name='account.analytic.plan.instance', string='Analytic Plan')

    @api.multi
    def button_confirm(self):
        super(AccountCashStatementRegister, self).button_confirm()
        for line in self.line_ids:
            if line.concept:
                analytic_plan_id = self.analytic_plan_id.id
                if line.concept:
                    analytic_plan_id = line.concept.analytic_plan_id.id
                line.bank_statement_line.analytics_id = analytic_plan_id
