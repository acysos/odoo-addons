# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
import json
import requests
import logging
_logger = logging.getLogger(__name__)


class NavarraMixin(models.AbstractModel):
    _name = "l10n.es.navarra.mixin"
    _description = "Mixin for Navarra specific functionalities"

    IAP_URL = "https://navarradoo.com/navarra_iap/"
    IAP_URL_2 = "https://server2.navarradoo.com/navarra_iap/"
    IAP_URL_3 = "https://server3.navarradoo.com/navarra_iap/"
    IAP_URL_4 = "https://server4.navarradoo.com/navarra_iap/"
    IAP_URL_5 = "https://acysos.com/navarra_iap/"
    VERSION = "0.1.5"

    def _get_initial_data(self, iap_name="L10n ES Navarra"):
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        data = {
            'license': json.dumps({
                'iap_key': self.env.company.navarra_iap_key,
                'db_uuid': db_uuid,
                'vat': self.env.company.vat,
                'iap_name': iap_name,
            }),
            'version': self.VERSION,
        }
        return data

    def _get_response(self, endpoint, data):
        try:
            response = requests.post(self.IAP_URL + endpoint, data=data)
        except requests.exceptions.RequestException as e:
            response = None
            _logger.info("Error connecting to IAP URL %s: %s", self.IAP_URL, e)
        if not response:
            try:
                response = requests.post(self.IAP_URL_2 + endpoint, data=data)
            except requests.exceptions.RequestException as e:
                response = None
                _logger.info("Error connecting to IAP URL %s: %s", self.IAP_URL_2, e)
        if not response:
            try:
                response = requests.post(self.IAP_URL_3 + endpoint, data=data)
            except requests.exceptions.RequestException as e:
                response = None
                _logger.info("Error connecting to IAP URL %s: %s", self.IAP_URL_3, e)
        if not response:
            try:
                response = requests.post(self.IAP_URL_4 + endpoint, data=data)
            except requests.exceptions.RequestException as e:
                response = None
                _logger.info("Error connecting to IAP URL %s: %s", self.IAP_URL_4, e)
        if not response:
            try:
                response = requests.post(self.IAP_URL_5 + endpoint, data=data)
            except requests.exceptions.RequestException as e:
                response = None
                _logger.info("Error connecting to IAP URL %s: %s", self.IAP_URL_5, e)
        return response


