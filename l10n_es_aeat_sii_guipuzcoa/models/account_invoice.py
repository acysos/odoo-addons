# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_sii_map(self):
        self.ensure_one()
        if self.company_id.state_id.code == 'SS':
            sii_map_obj = self.env['aeat.sii.map']
            sii_map_line_obj = self.env['aeat.sii.map.lines']
            sii_map = sii_map_obj.search(
                [('state', '=', self.company_id.state_id.id),
                 '|',
                 ('date_from', '<=', fields.Date.today()),
                 ('date_from', '=', False),
                 '|',
                 ('date_to', '>=', fields.Date.today()),
                 ('date_to', '=', False)], limit=1)
            if not sii_map:
                raise exceptions.Warning(_(
                    'SII Map not found. Check your configuration'))
            return sii_map
        else:
            return super(AccountInvoice, self)._get_sii_map()

    @api.multi
    def _get_test_mode(self, port_name):
        self.ensure_one()
        if self.company_id.state_id.code == 'SS' and self.company_id.sii_test:
            return port_name
        else:
            return super(AccountInvoice, self)._get_test_mode(port_name)

    @api.multi
    def _connect_wsdl(self, wsdl, port_name):
        self.ensure_one()
        company = self.company_id
        sii_map = self._get_sii_map()
        if company.state_id.code == 'SS' and company.sii_test:
            client = self._connect_sii(wsdl)
            client._default_service_name = 'siiService'
            port_name = self._get_test_mode(port_name)
            client._default_port_name = port_name
            if sii_map.version == '1.0':
                binding_name = '{'+wsdl.replace('v1.0/', '')+'}siiBinding'
            else:
                binding_name = '{'+wsdl.replace('v1.1/', '')+'}siiBinding'
            url = False
            if port_name == 'SuministroFactEmitidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_out.20', False)
            if port_name == 'SuministroFactRecibidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_in.20', False)
            if port_name == 'SuministroCobrosEmitidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_pr.20', False)
            if port_name == 'SuministroPagosRecibidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_ps.20', False)
            if url:
                return client.create_service(binding_name, url)
            else:
                return super(AccountInvoice, self)._connect_wsdl(
                    wsdl, port_name)
        else:
            return super(AccountInvoice, self)._connect_wsdl(wsdl, port_name)
