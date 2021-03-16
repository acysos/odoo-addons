# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AeatSiiPaymentModeKey(models.Model):
    _name = 'aeat.sii.payment.mode.key'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name')

    def name_get(self):
        vals = []
        for record in self:
            name = '[{}]-{}'.format(record.code, record.name)
            vals.append(tuple([record.id, name]))
        return vals


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    sii_key = fields.Many2one(
        comodel_name='aeat.sii.payment.mode.key',
        string="SII key", required=True)
