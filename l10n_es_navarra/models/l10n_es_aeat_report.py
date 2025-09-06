# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    is_navarra_model = fields.Boolean(
        string="Is Navarra Model",
        compute="_compute_is_navarra_model",
    )

    def _compute_is_navarra_model(self):
        """Compute if the model is a Navarra model."""
        company = self.env.company
        navarra_tax_agency = self.env.ref(
            "l10n_es_aeat.aeat_tax_agency_navarra")
        for record in self:
            if self.env.company.tax_agency_id.id == navarra_tax_agency.id and record.number in ["669", "349", "347"]:
                record.is_navarra_model = True
            else:
                record.is_navarra_model = False
