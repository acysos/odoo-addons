# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
from odoo import _, api, exceptions, fields, models
import json

ENDPOINT = 'f69'


class L10nESAeatTaxLine(models.Model):
    _inherit = 'l10n.es.aeat.tax.line'

    field_number_navarra = fields.Char(string='Field Number')
    name_navarra = fields.Char(string='Name')


class L10nEsNavarraModF69Report(models.Model):
    _name = "l10n.es.navarra.modf69.report"
    _inherit = ["l10n.es.aeat.report.tax.mapping", "l10n.es.navarra.mixin"]
    _description = "Navarra F69-F66 Report"
    _aeat_number = "669" # F69 en Navarra

    allow_posting = fields.Boolean(
        string="Allow posting",
        readonly=True,
    )
    total_devengado = fields.Float(
        string="[20] VAT payable",
        readonly=True,
    )
    total_deducir = fields.Float(
        string="[50] VAT receivable",
        readonly=True,
    )
    casilla_55 = fields.Float(
        string="[55] Relative percentage",
        default=1,
    )
    casilla_61 = fields.Float(
        string="[61] General scheme result",
        readonly=True,
    )
    previous_result = fields.Float(
        string="[62] To be deducted from the previous period",
    )
    resultado_liquidacion = fields.Float(
        string="[63] Settlement result",
        compute='_compute_resultado_liquidacion',
        readonly=True,
        store=True,
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
            ('7', 'Sólo en declaraciones que salen a pagar. Domiciliación del pago en cuenta bancaria del declarante'),
        ],
        string='Payment method',
        default='0',
    )
    casilla_93 = fields.Boolean(
        string="[93] Without activity",
        help="Check this box if not activity has been carried out during the period",
    )
    casilla_129 = fields.Boolean(
        string="[129] Last declaration",
        help="Check this box if this is the last declaration, closed the activity or transferred the business",
    )
    casilla_164 = fields.Boolean(
        string="[164] Operation with more than 3.005,06 €",
        help="Check this box if the total amount of operations with the same person or entity exceeds 3.005,06 €",
    )
    casilla_264 = fields.Boolean(
        string="[264] Exempt operations without right to deduction",
        help="Check this box if you have carried out exempt operations without right to deduction",
    )
    casilla_266 = fields.Boolean(
        string="[266] Simplified regime",
        help="Check this box if you do activities subject to the simplified regime",
    )

    def _compute_allow_posting(self):
        for report in self:
            report.allow_posting = True

    @api.model_create_multi
    def create(self, vals):
        if 'statement_type' in vals and vals['statement_type'] == 'C':
            raise exceptions.UserError("The statement type 'C' is not allowed in the Navarra F69 report")
        return super().create(vals)

    def write(self, vals):
        if 'statement_type' in vals and vals['statement_type'] == 'C':
            raise exceptions.UserError("The statement type 'C' is not allowed in the Navarra F69 report")
        return super().write(vals)

    @api.model
    def _report_identifier_get(self, vals):
        res = super()._report_identifier_get(vals)
        if '669' in res:
            if 'period_type' in vals and vals['period_type'] in ['1T', '2T', '3T', '4T']:
                res = res.replace('669', 'F69')
            else:
                res = res.replace('669', 'F66')
        return res

    def calculate(self):
        res = super().calculate()
        self._calculate_f69()
        return res

    def _calculate_f69(self):
        for modf69 in self:
            modf69.tax_line_ids.unlink()
            modf69.env.invalidate_all()
            data_taxes = []
            move_lines_taxes = self.env['account.move.line'].search([
                ('date', '>=', modf69.date_start),
                ('date', '<=', modf69.date_end),
                ('tax_line_id', '!=', False),
                ('parent_state', '=', 'posted'),
            ])
            for move_line in move_lines_taxes:
                data_taxes.append({
                    'id': move_line.id,
                    'tax_external_id': list(move_line.tax_line_id.get_external_id().values())[0].replace(
                        'l10n_es.'+str(self.env.company.id)+'_', ''),
                    'debit': move_line.debit,
                    'credit': move_line.credit,
                    'partner_id': move_line.partner_id.id,
                    'move_type': move_line.move_id.move_type,
                    'account_code': move_line.account_id.code[:3],
                })
            data_base = []
            move_lines_base = self.env['account.move.line'].search([
                ('date', '>=', modf69.date_start),
                ('date', '<=', modf69.date_end),
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

                    tax_external_id = list(tax.get_external_id().values())[0].replace(
                        'account.'+str(self.env.company.id)+'_', '')
                    while "account." in tax_external_id:
                        tax_external_id = tax_external_id.replace(
                            'account.', '')

                    data_base.append({
                        'id': move_line.id,
                        'tax_external_id': tax_external_id,
                        'debit': move_line.debit,
                        'credit': move_line.credit,
                        'partner_id': move_line.partner_id.id,
                        'move_type': move_line.move_id.move_type,
                        'account_code': move_line.account_id.code[:3],
                    })
            
            data_annual_taxes = []
            data_annual_base = []
            if modf69.period_type in ['4T', '12']:
                date_start_annual = modf69.date_end.replace(month=1, day=1)
                move_lines_annual_taxes = self.env['account.move.line'].search([
                    ('date', '>=', date_start_annual),
                    ('date', '<=', modf69.date_end),
                    ('tax_line_id', '!=', False),
                    ('parent_state', '=', 'posted'),
                ])
                for move_line in move_lines_annual_taxes:
                    data_annual_taxes.append({
                        'id': move_line.id,
                        'tax_external_id': list(move_line.tax_line_id.get_external_id().values())[0].replace(
                            'l10n_es.'+str(self.env.company.id)+'_', ''),
                        'debit': move_line.debit,
                        'credit': move_line.credit,
                        'partner_id': move_line.partner_id.id,
                        'move_type': move_line.move_id.move_type,
                        'account_code': move_line.account_id.code[:3],
                    })
                
                move_lines_annual_base = self.env['account.move.line'].search([
                    ('date', '>=', date_start_annual),
                    ('date', '<=', modf69.date_end),
                    ('tax_ids', '!=', False),
                    ('parent_state', '=', 'posted'),
                ])
                for move_line in move_lines_annual_base:
                    for tax in move_line.tax_ids:
                        manual_tax_line = self.env['account.tax.manual.navarra'].search([
                            ('company_id', '=', self.env.company.id),
                            ('manual_tax_id', '=', tax.id),
                        ], limit=1)
                        if manual_tax_line:
                            tax = manual_tax_line.original_tax_id

                        tax_external_id = list(tax.get_external_id().values())[0].replace(
                            'account.'+str(self.env.company.id)+'_', '')
                        while "account." in tax_external_id:
                            tax_external_id = tax_external_id.replace(
                                'account.', '')

                        data_annual_base.append({
                            'id': move_line.id,
                            'tax_external_id': tax_external_id,
                            'debit': move_line.debit,
                            'credit': move_line.credit,
                            'partner_id': move_line.partner_id.id,
                            'move_type': move_line.move_id.move_type,
                            'account_code': move_line.account_id.code[:3],
                        })

            data = self._get_initial_data(iap_name="F69-F66 Calculate")
            data.update({
                'period_type': modf69.period_type,
                'year': modf69.year,
                'date_start': modf69.date_start,
                'date_end': modf69.date_end,
                'report_id': modf69.id,
                'map_tax_line_id': self.env.ref('l10n_es_navarra.navarradoo_f69_2024_10_map_line_01').id,
                'casilla_55': modf69.casilla_55,
                'data_taxes': json.dumps(data_taxes),
                'data_base': json.dumps(data_base),
                'data_annual_taxes': json.dumps(data_annual_taxes),
                'data_annual_base': json.dumps(data_annual_base),
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
                            'l10n_es_navarra.navarradoo_f69_2024_10_map_line_02'
                        ).id
                    res_id = self.env['l10n.es.aeat.tax.line'].create(tax_line)
                modf69_vals = {
                    'total_devengado': result.get("total_devengado"),
                    'total_deducir': result.get("total_deducible"),
                    'casilla_61': result.get("casilla_61"),
                    'allow_posting': result.get("allow_posting"),
                }
                counterpart_account_code = result.get("counterpart_account_code")
                counterpart_account_id = self.env['account.account'].search([
                    ("code", "=like", counterpart_account_code+'%'),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if counterpart_account_id:
                    modf69_vals['counterpart_account_id'] = counterpart_account_id.id
                if 'casilla_164' in result:
                    modf69_vals['casilla_164'] = result['casilla_164']
                if 'casilla_93' in result:
                    modf69_vals['casilla_93'] = result['casilla_93']
                modf69.write(modf69_vals)
        return True

    @api.depends("casilla_61", "previous_result")
    def _compute_resultado_liquidacion(self):
        for report in self:
            report.resultado_liquidacion = report.currency_id.round(
                report.casilla_61 - report.previous_result
            )

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

    def _prepare_regularization_extra_move_lines(self):
        """Include behavior for the regularization of the fees to compensate."""
        lines = super()._prepare_regularization_extra_move_lines()
        return lines