# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_test_mode(self, port_name):
        self.ensure_one()
        if self.company_id.state_id.code == 'BI' and self.company_id.sii_test:
            return port_name
        else:
            return super(AccountInvoice, self)._get_test_mode(port_name)

    @api.multi
    def _get_wsdl(self, key):
        self.ensure_one()
        if self.company_id.state_id.code == 'BI':
            return self.env['ir.config_parameter'].get_param(key+'.48', False)
        else:
            return super(AccountInvoice, self)._get_wsdl(key)
