# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _connect_wsdl(self, wsdl, port_name):
        self.ensure_one()
        company = self.company_id
        if company.state_id.code == 'NA' or company.state_id.code == '31':
            client = self._connect_sii(wsdl)
            client._default_service_name = 'siiService'
            port_name = self._get_test_mode(port_name)
            client._default_port_name = port_name
            # Navarra temporal fix
            wsdl2 = wsdl.replace(
                'https://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_1_1/',
                'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/'
            )
            binding_name = '{'+wsdl2+'}siiBinding'
            if company.sii_test:
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap_test.31', False)
            else:
                url = self.env['ir.config_parameter'].get_param(
                    'l10n_es_aeat_sii.url_soap.31', False)
            return client.create_service(binding_name, url)
        else:
            return super(AccountInvoice, self)._connect_wsdl(wsdl, port_name)
