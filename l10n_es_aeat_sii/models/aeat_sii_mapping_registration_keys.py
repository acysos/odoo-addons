# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AeatSiiMappingRegistrationKeys(models.Model):
    _name = 'aeat.sii.mapping.registration.keys'
    _description = 'Aeat SII Invoice Registration Keys'

    # registration_id = fields.Many2one('aeat.sii.invoice.registration',
    # 'Aeat SII Invoice Registration')
    code = fields.Char(string='Code', required=True, size=2)
    name = fields.Char(string='Name', required=True)
    # type = fields.Selection([('sale','Sale'),('purchase','Purchase'),
    # ('all','All')],'Type',required=True)
    type = fields.Selection(
        selection=[('sale', 'Sale'), ('purchase', 'Purchase')], string='Type',
        required=True)

    def name_get(self):
        vals = []
        for record in self:
            name = '[{}]-{}'.format(record.code, record.name)
            vals.append(tuple([record.id, name]))
        return vals
