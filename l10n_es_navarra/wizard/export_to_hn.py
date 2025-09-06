# Copyright 2025 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests

from odoo import _, api, exceptions, fields, models
import json
import base64

ENDPOINT = 'export_file'


class L10nEsNavarraReportExportToHN(models.TransientModel):
    _name = "l10n.es.navarra.report.export_to_hn"
    _inherit = "l10n.es.navarra.mixin"
    _description = "Export Report to Hacienda Navarra Format"

    name = fields.Char(string="File name", readonly=True)
    data = fields.Binary(string="File", readonly=True)
    state = fields.Selection(
        selection=[("open", "open"), ("get", "get")], default="open"
    )

    def action_get_file(self):
        active_id = self.env.context.get("active_id", False)
        active_model = self.env.context.get("active_model", False)
        if not active_id or not active_model:
            return False
        report = self.env[active_model].browse(active_id)
        data = self._get_initial_data(iap_name='File Export')
        data.update({
            'name': report.name,
            'year': str(report.year),
            'date_start': report.date_start,
            'date_end': report.date_end,
            'company_vat': report.company_id.vat,
            'company_name': report.company_id.name,
            'contact_name': report.contact_name,
            'contact_email': report.contact_email,
            'contact_phone': report.contact_phone,
            'statement_type': report.statement_type,
            'support_type': report.support_type,
            'previous_number': report.previous_number or '',
            'representative_vat': report.representative_vat or '',
            'period_type': report.period_type,
        })

        partner_bank_acc_number = 20*"0"
        # if report.partner_bank_id and report.partner_bank_id.acc_number:
        #     partner_bank_acc_number = report.partner_bank_id.acc_number.replace(' ', '')
        #     if partner_bank_acc_number[0:2] == 'ES':
        #         partner_bank_acc_number = partner_bank_acc_number[4:]

        if report._name == 'l10n.es.navarra.modf69.report':
            if report.period_type in ['1T', '2T', '3T', '4T']:
                data['model_number'] = 'F69'
            else:
                data['model_number'] = 'F66'
            data['total_devengado'] = report.total_devengado
            data['total_deducir'] = report.total_deducir
            data['casilla_55'] = report.casilla_55
            data['casilla_61'] = report.casilla_61
            data['previous_result'] = report.previous_result
            data['resultado_liquidacion'] = report.resultado_liquidacion
            data['period_type_conversion'] = report.period_type_conversion
            data['payment_method'] = report.payment_method
            data['casilla_93'] = '1' if report.casilla_93 else '0'
            data['casilla_129'] = '1' if report.casilla_129 else '0'
            data['casilla_164_si'] = '1' if report.casilla_129 else '0'
            data['casilla_164_no'] = '1' if not report.casilla_129 else '0'
            data['casilla_264'] = '1' if report.casilla_264 else '0'
            data['casilla_265'] = '1' if not report.casilla_264 else '0'
            data['casilla_266'] = '1' if report.casilla_266 else '0'
            data['casilla_267'] = '1' if not report.casilla_266 else '0'
            data['partner_bank_acc_number'] = partner_bank_acc_number

            data_lines = []
            for line in report.tax_line_ids:
                data_line = {
                    'field_number': line.field_number_navarra,
                    'name': line.name_navarra,
                    'amount': line.amount,
                    'to_regularize': line.to_regularize,
                }
                data_lines.append(data_line)
            data['data_lines'] = json.dumps(data_lines)

        if report._name == 'l10n.es.aeat.mod347.report':
            data['model_number'] = '347'
            data['statement_type'].replace("N", " ")
            data['total_partner_records'] = report.total_partner_records
            data['total_amount'] = report.total_amount
            data['total_real_estate_records'] = report.total_real_estate_records
            data['total_real_estate_amount'] = report.total_real_estate_amount

            partner_record_data = []
            for line in report.partner_record_ids:
                data_line = {
                    'year': str(line.report_id.year),
                    'company_vat': line.report_id.company_id.vat,
                    'partner_vat': line.partner_vat,
                    'representative_vat': line.representative_vat or '',
                    'partner_name': line.partner_id.name,
                    'partner_state_code': line.partner_state_code,
                    'partner_country_code': line.partner_country_code if line.partner_state_code == '99' else '',
                    'operation_key': line.operation_key,
                    'amount': line.amount,
                    'insurance_operation': line.insurance_operation,
                    'bussiness_real_estate_rent': line.bussiness_real_estate_rent,
                    'cash_amount': line.cash_amount,
                    'real_estate_transmissions_amount': line.real_estate_transmissions_amount,
                    'origin_year': line.origin_year or line.report_id.year if line.cash_amount else '0000',
                    'first_quarter': line.first_quarter,
                    'first_quarter_real_estate_transmission': line.first_quarter_real_estate_transmission,
                    'second_quarter': line.second_quarter,
                    'second_quarter_real_estate_transmission': line.second_quarter_real_estate_transmission,
                    'third_quarter': line.third_quarter,
                    'third_quarter_real_estate_transmission': line.third_quarter_real_estate_transmission,
                    'fourth_quarter': line.fourth_quarter,
                    'fourth_quarter_real_estate_transmission': line.fourth_quarter_real_estate_transmission,
                    'community_vat': line.community_vat,
                    'cash_basis_operation': line.cash_basis_operation,
                    'tax_person_operation': line.tax_person_operation,
                    'related_goods_operation': line.related_goods_operation,
                }
                partner_record_data.append(data_line)
            data['partner_record_data'] = json.dumps(partner_record_data)

            real_estate_record_data = []
            for line in report.real_estate_record_ids:
                data_line = {
                    'year': str(line.report_id.year),
                    'company_vat': line.report_id.company_id.vat,
                    'partner_vat': line.partner_vat,
                    'representative_vat': line.representative_vat or '',
                    'partner_name': line.partner_id.name,
                    'amount': line.amount,
                    'situation': line.situation,
                    'reference': line.reference,
                    'address_type': line.address_type,
                    'address': line.address,
                    'number_type': line.number_type,
                    'number': line.number,
                    'number_calification': line.number_calification,
                    'block': line.block,
                    'portal': line.portal,
                    'stairway': line.stairway,
                    'floor': line.floor,
                    'door': line.door,
                    'complement': line.complement,
                    'city': line.city,
                    'township': line.township,
                    'township_code': line.township_code,
                    'state_code': line.state_code,
                    'postal_code': line.postal_code,
                }
                real_estate_record_data.append(data_line)
            data['real_estate_record_data'] = json.dumps(real_estate_record_data)

        if report._name == 'l10n.es.aeat.mod349.report':
            data['model_number'] = '349'
            data['total_partner_records'] = report.total_partner_records
            data['total_partner_records_amount'] = report.total_partner_records_amount
            data['total_partner_refunds'] = report.total_partner_refunds
            data['total_partner_refunds_amount'] = report.total_partner_refunds_amount

            partner_record_data = []
            for line in report.partner_record_ids:
                data_line = {
                    'year': str(line.report_id.year),
                    'company_vat': line.report_id.company_id.vat,
                    'partner_vat': line.partner_vat,
                    'partner_name': line.partner_id.name,
                    'operation_key': line.operation_key,
                    'total_operation_amount': line.total_operation_amount,
                }
                partner_record_data.append(data_line)
            data['partner_record_data'] = json.dumps(partner_record_data)

            partner_refund_data = []
            for line in report.partner_refund_ids:
                data_line = {
                    'report_year': str(line.report_id.year),
                    'company_vat': line.report_id.company_id.vat,
                    'partner_vat': line.partner_vat,
                    'partner_name': line.partner_id.name,
                    'year': str(line.year),
                    'period_type': line.period_type,
                    'total_operation_amount': line.total_operation_amount,
                    'total_origin_amount': line.total_origin_amount,
                }
                partner_refund_data.append(data_line)
            data['partner_refund_data'] = json.dumps(partner_refund_data)

        response = requests.post(self.IAP_URL + ENDPOINT, data=data)
        if response.status_code != 200:
            raise exceptions.UserError(
                _("Error in the IAP service: %s") % response.reason
            )
        result = response.json()
        if result.get("status") == "error":
            raise exceptions.UserError(
                _("Error in the IAP service: %s") % result.get("error")
            )
        else:
            file = base64.encodebytes(result['contents'].encode('iso-8859-1'))
            file_name = result['file_name']
            # Delete old files
            attachment_obj = self.env["ir.attachment"]
            attachment_ids = attachment_obj.search(
                [("name", "=", file_name), ("res_model", "=", report._name)]
            )
            attachment_ids.unlink()
            attachment_obj.create(
                {
                    "name": file_name,
                    "datas": file,
                    "res_model": report._name,
                    "res_id": report.id,
                }
            )
            self.write({"state": "get", "data": file, "name": file_name})
            data_obj = self.env.ref("l10n_es_aeat.wizard_aeat_export")
            return {
                "type": "ir.actions.act_window",
                "res_model": self._name,
                "view_mode": "form",
                "view_id": [data_obj.id],
                "res_id": self.id,
                "target": "new",
            }
