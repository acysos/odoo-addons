# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
import json

ENDPOINT = '715'


class L10nEsNavarraMod715Report(models.Model):
    _name = "l10n.es.navarra.mod715.report"
    _inherit = ["l10n.es.aeat.report.tax.mapping", "l10n.es.navarra.mixin"]
    _description = "Navarra 715-745 Report"
    _aeat_number = "715"

    allow_posting = fields.Boolean(
        string="Allow posting",
        readonly=True,
    )
    casilla_01 = fields.Float(
        string="[01] Amount to pay",
    )
    period_type_conversion = fields.Char(
        string='Period type conversion',
        compute='_compute_period_type_conversion',
        readonly=True,
    )
    payment_method = fields.Selection(
        selection=[
            ('0', 'Indica la no solicitud de la tramitación del pago'),
            ('1', 'Sólo en declaraciones que salen a pagar. Indica que se solicita que Hacienda tramite con la entidad'
                  ' bancaria el pago en nombre propio de la declaración telemáticamente'),
            ('2', 'Sólo en declaraciones que salen a pagar. Indica que se solicita que Hacienda tramite con la entidad'
                  ' bancaria el pago actuando el presentador en representación del declarante de la declaración telemáticamente'),
            ('3', 'Sólo en declaraciones que salen a pagar. Indica que se solicita que Hacienda tramite con la entidad'
                  ' bancaria el pago por provisión de fondos por parte del presentador de la declaración telemáticamente'),
            ('4', 'Solicitud de aplazamiento'),
            ('5', 'Solicitud de compensación'),
            ('6', 'Pago mediante carta de pago'),
            ('7', 'Sólo en declaraciones que salen a pagar. Domiciliación del pago en cuenta bancaria del declarante'),
        ],
        string='Payment method',
        default='0',
    )

    def _compute_allow_posting(self):
        for report in self:
            report.allow_posting = True

    @api.model
    def _report_identifier_get(self, vals):
        res = super()._report_identifier_get(vals)
        if '715' in res:
            if 'period_type' in vals and vals['period_type'] not in ['1T', '2T', '3T', '4T']:
                res = res.replace('715', '745')
        return res

    def calculate(self):
        res = super().calculate()
        self._calculate_715()
        return res

    def _calculate_715(self):
        for mod715 in self:
            mod715.tax_line_ids.unlink()
            mod715.env.invalidate_all()
            data_taxes = []
            move_lines_taxes = self.env['account.move.line'].search([
                ('date', '>=', mod715.date_start),
                ('date', '<=', mod715.date_end),
                ('tax_line_id', '!=', False),
                ('parent_state', '=', 'posted'),
            ])
            for move_line in move_lines_taxes:
                tax = move_line.tax_line_id
                manual_tax_line = self.env['account.tax.manual.navarra'].search([
                    ('company_id', '=', self.env.company.id),
                    ('manual_tax_id', '=', tax.id),
                ], limit=1)
                if manual_tax_line:
                    tax = manual_tax_line.original_tax_id
                tax_external_id = (
                    list(tax.get_external_id().values())[0]
                    .replace('l10n_es.' + str(self.env.company.id) + '_', '')
                    .replace('account.' + str(self.env.company.id) + '_', '')
                )
                while "l10n_es." in tax_external_id:
                    tax_external_id = tax_external_id.replace('l10n_es.', '')
                while "account." in tax_external_id:
                    tax_external_id = tax_external_id.replace('account.', '')
                data_taxes.append({
                    'id': move_line.id,
                    'tax_external_id': tax_external_id,
                    'debit': move_line.debit,
                    'credit': move_line.credit,
                    'partner_id': move_line.partner_id.id,
                    'move_type': move_line.move_id.move_type,
                    'account_code': move_line.account_id.code[:3],
                })
            data_base = []
            move_lines_base = self.env['account.move.line'].search([
                ('date', '>=', mod715.date_start),
                ('date', '<=', mod715.date_end),
                ('tax_ids', '!=', False),
                ('parent_state', '=', 'posted'),
            ])
            for move_line in move_lines_base:
                for tax in move_line.tax_ids:
                    manual_tax_line = self.env['account.tax.manual.navarra'].search([
                        ('company_id', '=', self.env.company.id),
                        ('manual_tax_id', '=', tax.id),
                    ], limit=1)
                    if manual_tax_line:
                        tax = manual_tax_line.original_tax_id
                    tax_external_id = (
                        list(tax.get_external_id().values())[0]
                        .replace('l10n_es.' + str(self.env.company.id) + '_', '')
                        .replace('account.' + str(self.env.company.id) + '_', '')
                    )
                    while "l10n_es." in tax_external_id:
                        tax_external_id = tax_external_id.replace('l10n_es.', '')
                    while "account." in tax_external_id:
                        tax_external_id = tax_external_id.replace('account.', '')
                    data_base.append({
                        'id': move_line.id,
                        'tax_external_id': tax_external_id,
                        'debit': move_line.debit,
                        'credit': move_line.credit,
                        'partner_id': move_line.partner_id.id,
                        'move_type': move_line.move_id.move_type,
                        'account_code': move_line.account_id.code[:3],
                    })

            data = self._get_initial_data(iap_name="715-745 Calculate")
            data.update({
                'period_type': mod715.period_type,
                'year': mod715.year,
                'date_start': mod715.date_start,
                'date_end': mod715.date_end,
                'report_id': mod715.id,
                'map_tax_line_id': self.env.ref('l10n_es_navarra.navarradoo_715_2025_11_map_line_01').id,
                'data_taxes': json.dumps(data_taxes),
                'data_base': json.dumps(data_base),
            })
            response = self._get_response(ENDPOINT, data)
            if not response:
                raise exceptions.UserError(
                    _("Error connecting to the IAP service. Please try again later.")
                )
            if response.status_code != 200:
                raise exceptions.UserError(
                    _("Error in the IAP service: %s") % response.reason
                )
            result = response.json()
            if result.get("status") != "ok":
                raise exceptions.UserError(
                    _("Error in the IAP service: %s") % result.get("error")
                )
            else:
                tax_lines = result.get("tax_lines")
                for tax_line in tax_lines:
                    if 'to_regularize' in tax_line and tax_line['to_regularize']:
                        tax_line['map_line_id'] = self.env.ref(
                            'l10n_es_navarra.navarradoo_715_2025_11_map_line_02'
                        ).id
                    self.env['l10n.es.aeat.tax.line'].create(tax_line)
                mod715_vals = {
                    'casilla_01': result.get("casilla_01"),
                    'allow_posting': result.get("allow_posting"),
                }
                counterpart_account_code = result.get("counterpart_account_code")
                counterpart_account_id = self.env['account.account'].search([
                    ("code", "=like", counterpart_account_code + '%'),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if counterpart_account_id:
                    mod715_vals['counterpart_account_id'] = counterpart_account_id.id
                mod715.write(mod715_vals)
        return True

    @api.depends("period_type")
    def _compute_period_type_conversion(self):
        for report in self:
            if "T" in report.period_type:
                report.period_type_conversion = report.period_type.replace("T", "00")
            else:
                if report.period_type in ["01", "02", "03"]:
                    period_prefix = "1"
                elif report.period_type in ["04", "05", "06"]:
                    period_prefix = "2"
                elif report.period_type in ["07", "08", "09"]:
                    period_prefix = "3"
                else:
                    period_prefix = "4"
                report.period_type_conversion = period_prefix + report.period_type

