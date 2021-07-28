# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions, _
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_sii_map(self):
        self.ensure_one()
        _logger.info(self.company_id.state_id.code)
        if self.company_id.state_id.code == 'BI':
            _logger.info("Vizcaya State")
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
            _logger.info(50*"=")
            _logger.info(sii_map)
            return sii_map
        else:
            return super(AccountMove, self)._get_sii_map()

    def _get_test_mode(self, port_name):
        self.ensure_one()
        if self.company_id.state_id.code == 'BI' and self.company_id.sii_test:
            return port_name
        else:
            return super(AccountMove, self)._get_test_mode(port_name)

    def _connect_wsdl(self, wsdl, port_name):
        self.ensure_one()
        company = self.company_id
        sii_map = self._get_sii_map()
        if company.state_id.code == 'BI' and company.sii_test:
            client = self._connect_sii(wsdl)
            client._default_service_name = 'siiService'
            port_name = self._get_test_mode(port_name)
            client._default_port_name = port_name
            if sii_map.version == '1.0':
                binding_name = '{'+wsdl.replace('v10/', '')+'}siiBinding'
            else:
                binding_name = '{'+wsdl+'}siiBinding'
            url = False
            if port_name == 'SuministroFactEmitidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_out.48', False)
            if port_name == 'SuministroFactRecibidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_in.48', False)
            if port_name == 'SuministroCobrosEmitidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_pr.48', False)
            if port_name == 'SuministroPagosRecibidas':
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_ps.48', False)
            if url:
                return client.create_service(binding_name, url)
            else:
                return super(AccountMove, self)._connect_wsdl(
                    wsdl, port_name)
        else:
            return super(AccountMove, self)._connect_wsdl(wsdl, port_name)

