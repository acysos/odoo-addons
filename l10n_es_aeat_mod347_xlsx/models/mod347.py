# Copyright 2019 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _

MAP_KEYS = {
    'A': 'A - Adquisiciones de bienes y servicios superiores al '
         'límite (1)',
    'B': 'B - Entregas de bienes y servicios superiores al límite (1)',
    'C': 'C - Cobros por cuenta de terceros superiores al límite (3)',
    'D': 'D - Adquisiciones efectuadas por Entidades Públicas '
         '(...) superiores al límite (1)',
    'E': 'E - Subvenciones, auxilios y ayudas satisfechas por Ad. '
          'Públicas superiores al límite (1)',
    'F': 'F - Ventas agencia viaje',
    'G': 'G - Compras agencia viaje'
}

STATE_KEYS = {
    'pending': _('Pending'),
    'sent': _('Sent'),
    'confirmed': _('Confirmed'),
    'exception': _('Exception'),
}

class L10nEsAeatMod347Report(models.Model):
    _inherit = 'l10n.es.aeat.mod347.report'

    def export_xls(self):
        module = __name__.split('addons.')[1].split('.')[0]
        report_name = '{}.aeat_mod347_xlsx'.format(module)
        report = {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': report_name,
            'context': dict(self.env.context, report_file='aeat_mod347'),
            'data': {'dynamic_report': True},
        }
        return report


class L10nEsAeatMod347PartnerRecord(models.Model):
    _inherit = 'l10n.es.aeat.mod347.partner_record'

    @api.depends('operation_key')
    def _get_operation_key_value(self):
        for record in self:
            if record.operation_key in MAP_KEYS:
                record.operation_key_value = MAP_KEYS[record.operation_key]

    @api.depends('state')
    def _get_state_value(self):
        for record in self:
            if record.state in STATE_KEYS:
                record.state_value = STATE_KEYS[record.state]

    operation_key_value = fields.Char(
        string='Operation Key Value', compute='_get_operation_key_value',
        store=True)
    state_value = fields.Char(
        string='State Value', compute='_get_state_value', store=True)
