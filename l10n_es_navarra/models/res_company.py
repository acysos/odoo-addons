# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    navarra_iap_key = fields.Char(
        string='Navarra IAP Key',
        help='Key to access the Navarra IAP service',
    )