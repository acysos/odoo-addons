# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    
    def change_cashdro(self):
        self.ensure_one()
        self.journal_id._cashdro_operation(
            '18', self.journal_id.name, self.journal_id.cashdro_ip, 
            self.journal_id.cashdro_user, self.journal_id.cashdro_password)
