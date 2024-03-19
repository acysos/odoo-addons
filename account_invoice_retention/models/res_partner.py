# -*- coding: utf-8 -*-
# © 2020 Ignacio Ibeas - Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    with_retention = fields.Boolean(
        string='With retention',
        help='This partner apply retention in invoices')
    retention_percentage = fields.Float(
        string='Retention Percentage')
    retention_days = fields.Integer(
        string='Retention Days')
