# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class AccountTaxManualNavarra(models.Model):
    _name = "account.tax.manual.navarra"

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company.id)
    manual_tax_id = fields.Many2one(
        'account.tax', string='Manual Tax', required=True)
    original_tax_id = fields.Many2one(
        'account.tax', string='Original Tax', required=True)
