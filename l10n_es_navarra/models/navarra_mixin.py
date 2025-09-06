# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
import json


class NavarraMixin(models.AbstractModel):
    _name = "l10n.es.navarra.mixin"
    _description = "Mixin for Navarra specific functionalities"

    IAP_URL = "https://navarradoo.com/navarra_iap/"
    VERSION = "0.1.3"

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

