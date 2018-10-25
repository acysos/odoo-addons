# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class res_company(models.Model):
    _inherit = 'res.company'

    account_expense = fields.Many2one(
        comodel_name='account.account', string='Account Expense',
        required=True)
    account_irpf = fields.Many2one(
        comodel_name='account.account', string='Account IRPF',
        required=True)
    account_ss = fields.Many2one(
        comodel_name='account.account', string='Account SS',
        required=True)
    tax_code_base = fields.Many2one(
        comodel_name='account.tax.code', string='Tax code base',
        required=True)
    tax_code_amount = fields.Many2one(
        comodel_name='account.tax.code', string='Tax code amount',
        required=True)
