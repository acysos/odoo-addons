# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_test_mode(self, port_name):
        self.ensure_one()
        if self.company_id.state_id.code == '20' and self.company_id.sii_test:
            return port_name
        else:
            return super(AccountInvoice, self)._get_test_mode(port_name)

    @api.multi
    def _connect_wsdl(self, wsdl, port_name):
        self.ensure_one()
        company = self.company_id
        if company.state_id.code == '20' and company.sii_test:
            client = self._connect_sii(wsdl)
            client._default_service_name = 'siiService'
            port_name = self._get_test_mode(port_name)
            client._default_port_name = port_name
            binding_name = '{'+wsdl+'}siiBinding'
            url = self.env['ir.config_parameter'].get_param(
                'l10n_es_aeat_sii.url_soap.20', False)
            return client.create_service(binding_name, url)
        else:
            return super(AccountInvoice, self)._connect_wsdl(wsdl, port_name)

    @api.multi
    def _get_wsdl(self, key):
        self.ensure_one()
        if self.company_id.state_id.code == '20':
            return self.env['ir.config_parameter'].get_param(key+'.20', False)
        else:
            return super(AccountInvoice, self)._get_wsdl(key)
