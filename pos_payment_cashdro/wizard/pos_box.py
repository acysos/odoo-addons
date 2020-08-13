# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import time
from odoo.addons.account.wizard.pos_box import CashBox

 
class CashDroBoxIn(CashBox):
    _inherit = 'cash.box.in'
  
    @api.multi
    def _calculate_values_for_statement_line(self, record):
        active_model = self.env.context.get('active_model', False)
        if active_model == 'pos.session':
            active_ids = self.env.context.get('active_ids', [])
            journal_env = self.env['account.journal']
            for session in self.env['pos.session'].browse(active_ids):
                if (record.journal_id.cashdro_payment_terminal 
                        and not self.env.context.get('pass_cashdro')):
                    response_data = journal_env._cashdro_operation(
                        '1', 'pos-' + session.name, session.config_id.cashdro_ip,
                        session.config_id.cashdro_user,
                        session.config_id.cashdro_password)
                    self.amount = int(response_data['total'])/100
                    ctx = self.env.context.copy()
                    ctx.update({'pass_cashdro': True})
                    return super(
                        CashDroBoxIn, self.with_context(
                            ctx))._calculate_values_for_statement_line(
                                record)
        else:
            return super(
                CashDroBoxIn, self)._calculate_values_for_statement_line(
                    record)
  
  
class CashDroBoxOut(CashBox):
    _inherit = 'cash.box.out'
  
    @api.multi
    def _calculate_values_for_statement_line(self, record):
        active_model = self.env.context.get('active_model', False)
        if active_model == 'pos.session':
            active_ids = self.env.context.get('active_ids', [])
            journal_env = self.env['account.journal']
            for session in self.env['pos.session'].browse(active_ids):
                if (record.journal_id.cashdro_payment_terminal 
                        and not self.env.context.get('pass_cashdro')):
                    response_data = journal_env._cashdro_operation(
                        '2', 'pos-' + session.name, session.config_id.cashdro_ip,
                        session.config_id.cashdro_user,
                        session.config_id.cashdro_password)
                    self.amount = int(response_data['total'])/100
                ctx = self.env.context.copy()
                ctx.update({'pass_cashdro': True})
                return super(
                    CashDroBoxOut, self.with_context(
                        ctx))._calculate_values_for_statement_line(
                            record)
        else:
            return super(
                CashDroBoxOut, self)._calculate_values_for_statement_line(
                    record)
