# -*- coding: utf-8 -*-
# © 2016 Ignacio Ibeas - Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    retention_percentage = fields.Float(string='Retention Percentage',
                                        default=0)
    retention_days = fields.Integer(string='Retention Days',
                                    default=0)
    retention_account = fields.Many2one(comodel_name='account.account',
                                        string='Retention Account')
    with_taxes = fields.Boolean(
        string='With taxes',
        help='The retention include the total with taxes')
