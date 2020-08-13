# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class account_payment(models.Model):
    _inherit = "account.payment"
    
    def action_validate_invoice_payment(self):
        journal_env = self.env['account.journal']
        for record in self:
            if record.journal_id.cashdro_payment_terminal:
                if record.partner_type == 'supplier':
                    response_data = journal_env._cashdro_operation(
                        '3', record.journal_id.name, 
                        record.journal_id.cashdro_ip,
                        record.journal_id.cashdro_user,
                        record.journal_id.cashdro_password, record.amount)
                    record.amount = int(response_data['total'])/100
                if record.partner_type == 'customer':
                    response_data = journal_env._cashdro_operation(
                        '4', record.journal_id.name, 
                        record.journal_id.cashdro_ip,
                        record.journal_id.cashdro_user,
                        record.journal_id.cashdro_password, record.amount)
                    record.amount = int(response_data['total'])/100
        return super(account_payment, self).action_validate_invoice_payment()