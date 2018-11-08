# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class res_company(models.Model):
    _inherit = 'res.company'

    payroll_journal = fields.Many2one(
        comodel_name='account.journal', string='Payroll journal', required=True)
    move_confirm = fields.Boolean(string='Auto move confirm?')
    payroll_payment_mode = fields.Many2one(
        comodel_name='account.payment.mode', string='Payroll Payment Mode')
