# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
from odoo import _, api, exceptions, fields, models
import json
import logging
_logger = logging.getLogger(__name__)

ENDPOINT = 'sii'


class AeatTaxAgency(models.Model):
    _name = "aeat.tax.agency"
    _inherit = ["aeat.tax.agency", "l10n.es.navarra.mixin"]

    def _connect_params_sii(self, mapping_key, company):
        self.ensure_one()
        res = super()._connect_params_sii(mapping_key, company)
        navarra_tax_agency = self.env.ref(
            "l10n_es_aeat.aeat_tax_agency_navarra")
        if navarra_tax_agency:
            if self.env.company.tax_agency_id.id == navarra_tax_agency.id:
                data = self._get_initial_data(iap_name="SII Data")
                data.update({
                    'mapping_key': mapping_key,
                    'sii_test': company.sii_test,
                })
                _logger.info("Data: %s", data)
                response = requests.post(self.IAP_URL + ENDPOINT, data=data)
                if response.status_code != 200:
                    raise exceptions.UserError(
                        _("Error in the IAP service: %s") % response.reason
                    )
                result = response.json()
                if result.get("status") != "ok":
                    raise exceptions.UserError(
                        _("Error in the IAP service: %s") % result.get("error")
                    )
                else:
                    res = {
                        "address": result.get("address"),
                        "port_name": result.get("port_name"),
                        "wsdl": result.get("wsdl"),
                    }
        return res
