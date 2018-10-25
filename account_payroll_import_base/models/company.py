# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class res_company(models.Model):
    _inherit = 'res.company'

    temp_file_path = fields.Char(string='Temp files path', required=True)
    payroll_journal = fields.Many2one(
        comodel_name='account.journal', string='Payroll journal', required=True)
    sheet_name = fields.Char(string='Sheet name', required=True)
    move_confirm = fields.Boolean(string='Auto move confirm?')
