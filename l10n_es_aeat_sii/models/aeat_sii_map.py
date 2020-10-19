# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo import exceptions


class AeatSiiMap(models.Model):
    _name = 'aeat.sii.map'
    _description = 'Aeat SII Map'

    @api.constrains('date_from', 'date_to')
    def _unique_date_range(self):
        # Based in l10n_es_aeat module
        self.ensure_one()
        domain = [('id', '!=', self.id), ('state', '=', self.state.id)]
        if self.date_from and self.date_to:
            domain += ['|',
                       ('date_from', '<=', self.date_to),
                       ('date_from', '>=', self.date_from),
                       '|',
                       ('date_to', '<=', self.date_to),
                       ('date_to', '>=', self.date_from),
                       '|',
                       ('date_from', '=', False),
                       ('date_to', '>=', self.date_from),
                       '|',
                       ('date_to', '=', False),
                       ('date_from', '<=', self.date_to),
                       ]
        elif self.date_from:
            domain += [('date_to', '>=', self.date_from)]
        elif self.date_to:
            domain += [('date_from', '<=', self.date_to)]
        date_lst = self.search(domain)
        if date_lst:
            raise exceptions.Warning(
                _("Error! The dates of the record overlap with an existing "
                  "record."))

    name = fields.Char(string='Model', required=True)
    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')
    version = fields.Char(string='Version')
    state = fields.Many2one(comodel_name='res.country.state')
    map_lines = fields.One2many(
        comodel_name='aeat.sii.map.lines',
        inverse_name='sii_map_id',
        string='Lines')
    wsdl_url = fields.One2many(
        comodel_name='aeat.sii.wsdl',
        inverse_name='sii_map_id')

    def _get_wsdl(self, key):
        self.ensure_one()
        sii_wsdl = self.wsdl_url.search(
            [('sii_map_id', '=', self.id), ('key', '=', key)], limit=1)
        if sii_wsdl:
            wsdl = sii_wsdl.wsdl
        else:
            raise exceptions.Warning(_(
                'WSDL not found. Check your configuration'))
        return wsdl


class AeatSiiMapLines(models.Model):
    _name = 'aeat.sii.map.lines'
    _description = 'Aeat SII Map Lines'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name')
    taxes = fields.Many2many(
        comodel_name='account.tax.template', string="Taxes")
    sii_map_id = fields.Many2one(
        comodel_name='aeat.sii.map',
        string='Aeat SII Map',
        ondelete='cascade')


class AeatSiiWsdl(models.Model):
    _name = 'aeat.sii.wsdl'
    _description = 'Aeat SII WDSL Urls'
    
    name = fields.Char(string='Name')
    key = fields.Char(string='Key', readonly=True)
    wsdl = fields.Char(string='WDSL Url')
    sii_map_id = fields.Many2one(
        comodel_name='aeat.sii.map',
        string='Aeat SII Map',
        ondelete='cascade')
