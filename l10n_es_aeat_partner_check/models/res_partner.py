# Copyright 2019 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _

RESULTS = [
    ('IDENTIFICADO', _('Identificado')),
    ('NO IDENTIFICADO', _('No identificado')),
    ('NO IDENTIFICADO-SIMILAR', _('No identificado Similar')),
    ('NO PROCESADO', _('No procesado')),
    ('NO IDENTIFICABLE', _('No identificable')),
    ('IDENTIFICADO-BAJA', _('Identificado Baja')),
    ('IDENTIFICADO-REVOCADO', _('Identificado Revocado'))
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends('aeat_partner_name', 'name')
    def _compute_data_diff(self):
        for partner in self.filtered('aeat_partner_check_result'):
            if partner.aeat_partner_check_result != 'NO IDENTIFICABLE':
                # Odoo don't support two space between name. Some names
                # in AEAT has two space instead one
                partner.aeat_data_diff = False
                if partner.aeat_partner_name:
                    if partner.name != partner.aeat_partner_name.replace(
                            '  ', ' '):
                        partner.aeat_data_diff = True

    aeat_partner_check_result = fields.Selection(
        selection=RESULTS, string='Check Result', readonly=True)
    aeat_partner_vat = fields.Char(string='VAT', readonly=True)
    aeat_partner_name = fields.Char(string='AEAT Name', readonly=True)
    aeat_data_diff = fields.Boolean(
        string='Data different', compute='_compute_data_diff', store=True)

    def get_test_mode(self, port_name):
        return port_name

    def aeat_check_partner(self):
        soap_obj = self.env['l10n.es.aeat.soap']
        service = 'VNifV2Service'
        wsdl = 'https://www2.agenciatributaria.gob.es/static_files/common/' + \
            'internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV2.wsdl'
        port_name = 'VNifPort1'
        operation = 'VNifV2'
        for partner in self:
            country_code, _, vat_number = partner._parse_aeat_vat_info()
            if country_code != 'ES':
                continue
            request = {
                'Nif': vat_number,
                'Nombre': partner.name
            }
            res = soap_obj.send_soap(
                service, wsdl, port_name, partner, operation, request)
            if res:
                partner.aeat_partner_vat = res[0]['Nif']
                partner.aeat_partner_name = res[0]['Nombre']
                partner.aeat_partner_check_result = res[0]['Resultado']
                if partner.aeat_partner_name != partner.name:
                    partner.aeat_data_diff = True
            else:
                partner.aeat_partner_vat = None
                partner.aeat_partner_name = None
                partner.aeat_partner_check_result = 'NO IDENTIFICABLE'

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'name' in vals or 'vat' in vals:
            for partner in self:
                if 'company_id' in vals:
                    company = self.env['res.company'].browse(vals['company_id'])
                elif partner.company_id:
                    company = partner.company_id
                else:
                    company = self.env.user.company_id
                if company.vat_check_aeat:
                    partner.aeat_check_partner()
        return res

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        if 'company_id' in vals:
            company = self.env['res.company'].browse(vals['company_id'])
        elif partner.company_id:
            company = partner.company_id
        else:
            company = self.env.user.company_id
        if company.vat_check_aeat:
            partner.aeat_check_partner()
        return partner
