# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import time
import webbrowser
from odoo.addons.account.wizard.pos_box import CashBox

 
class CashDroBoxIn(CashBox):
    _inherit = 'cash.box.in'
  
    @api.multi
    def _calculate_values_for_statement_line(self, record):
        if (record.journal_id.cashdro_payment_terminal 
                and not self.env.context.get('pass_cashdro')):
            response_data = self.env['account.journal']._cashdro_operation(
                '1', record.journal_id.name, record.journal_id.cashdro_ip,
                record.journal_id.cashdro_user,
                record.journal_id.cashdro_password)
            self.amount = int(response_data['total'])/100
        return super(
            CashDroBoxIn, self)._calculate_values_for_statement_line(record)
  
  
class CashDroBoxOut(CashBox):
    _inherit = 'cash.box.out'
  
    @api.multi
    def _calculate_values_for_statement_line(self, record):
        if (record.journal_id.cashdro_payment_terminal 
                and not self.env.context.get('pass_cashdro')):
            response_data = self.env['account.journal']._cashdro_operation(
                '2', record.journal_id.name, record.journal_id.cashdro_ip,
                record.journal_id.cashdro_user,
                record.journal_id.cashdro_password)
            self.amount = int(response_data['total'])/100
        return super(
            CashDroBoxOut, self)._calculate_values_for_statement_line(record)
