# Copyright 2019 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, _

class AeatMod347ExportXlsx(models.AbstractModel):
    _name = 'report.l10n_es_aeat_mod347_xlsx.aeat_mod347_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def _get_ws_params(self, wb, data, mod347s):
        
        mod347_template = {
            'operation_key': {
                'header': {
                    'value': _('Operation Key'),
                },
                'data': {
                    'value': self._render(
                        'mod347.partner_record_ids.operation_key_value'),
                },
                'width': 20,
            },
            'name': {
                'header': {
                    'value': _('Name'),
                },
                'data': {
                    'value': self._render(
                        'mod347.partner_record_ids.partner_id.name'),
                },
                'width': 20,
            },
            'partner_vat': {
                'header': {
                    'value': _('VAT'),
                },
                'data': {
                    'value': self._render(
                        'mod347.partner_record_ids.partner_vat'),
                },
                'width': 20,
            },
            'partner_country_code': {
                'header': {
                    'value': _('Country Code'),
                },
                'data': {
                    'value': self._render(
                        'mod347.partner_record_ids.partner_country_code'),
                },
                'width': 20,
            },
            'partner_state_code': {
                'header': {
                    'value': _('State Code'),
                },
                'data': {
                    'value': self._render(
                        'mod347.partner_record_ids.partner_state_code'),
                },
                'width': 20,
            },
            'amount': {
                'header': {
                    'value': _('Amount'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.amount'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'cash_amount': {
                'header': {
                    'value': _('Cash Amount'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.cash_amount'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'real_estate_transmissions_amount': {
                'header': {
                    'value': _('Real Estate Transmission Amount'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.' +
                        'real_estate_transmissions_amount'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'first_quarter': {
                'header': {
                    'value': _('1T'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.first_quarter'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'second_quarter': {
                'header': {
                    'value': _('2T'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.second_quarter'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'third_quarter': {
                'header': {
                    'value': _('3T'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.third_quarter'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'fourth_quarter': {
                'header': {
                    'value': _('4T'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.fourth_quarter'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'first_quarter_real_estate_transmission': {
                'header': {
                    'value': _('1T Real Estate'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.' +
                        'first_quarter_real_estate_transmission'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'second_quarter_real_estate_transmission': {
                'header': {
                    'value': _('2T Real Estate'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.' +
                        'second_quarter_real_estate_transmission'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'third_quarter_real_estate_transmission': {
                'header': {
                    'value': _('3T Real Estate'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.' +
                        'third_quarter_real_estate_transmission'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'fourth_quarter_real_estate_transmission': {
                'header': {
                    'value': _('4T Real Estate'),
                },
                'data': {
                    'type': 'number',
                    'value': self._render(
                        'mod347.partner_record_ids.' +
                        'fourth_quarter_real_estate_transmission'),
                    'format': self.format_amount_right,
                },
                'width': 20,
            },
            'state': {
                'header': {
                    'value': _('State'),
                },
                'data': {
                    'value': self._render(
                        'mod347.partner_record_ids.state_value'),
                },
                'width': 20,
            },
            'check_ok': {
                'header': {
                    'value': _('Record is OK'),
                },
                'data': {
                    'type': 'boolean',
                    'value': self._render(
                        'mod347.partner_record_ids.check_ok'),
                },
                'width': 20,
            },
            'insurance_operation': {
                'header': {
                    'value': _('Insurance Operation'),
                },
                'data': {
                    'type': 'boolean',
                    'value': self._render(
                        'mod347.partner_record_ids.insurance_operation'),
                },
                'width': 20,
            },
            'cash_basis_operation': {
                'header': {
                    'value': _('Cash Basis Operation'),
                },
                'data': {
                    'type': 'boolean',
                    'value': self._render(
                        'mod347.partner_record_ids.cash_basis_operation'),
                },
                'width': 20,
            },
            'tax_person_operation': {
                'header': {
                    'value': _('Taxable Person Operation'),
                },
                'data': {
                    'type': 'boolean',
                    'value': self._render(
                        'mod347.partner_record_ids.tax_person_operation'),
                },
                'width': 20,
            },
            'related_goods_operation': {
                'header': {
                    'value': _('Related Goods Operation'),
                },
                'data': {
                    'type': 'boolean',
                    'value': self._render(
                        'mod347.partner_record_ids.related_goods_operation'),
                },
                'width': 20,
            },
            'bussiness_real_estate_rent': {
                'header': {
                    'value': _('Bussiness Real Estate Rent'),
                },
                'data': {
                    'type': 'boolean',
                    'value': self._render(
                        'mod347.partner_record_ids.bussiness_real_estate_rent'),
                },
                'width': 20,
            },
        }
        
        wanted_list = [
            'operation_key', 'name', 'partner_vat', 'partner_country_code',
            'partner_state_code', 'amount', 'cash_amount',
            'real_estate_transmissions_amount', 'first_quarter',
            'second_quarter', 'third_quarter', 'fourth_quarter',
            'first_quarter_real_estate_transmission',
            'second_quarter_real_estate_transmission',
            'third_quarter_real_estate_transmission',
            'fourth_quarter_real_estate_transmission',
            'state', 'check_ok', 'insurance_operation', 'cash_basis_operation',
            'tax_person_operation', 'related_goods_operation',
            'bussiness_real_estate_rent']

        ws_params = {
            'ws_name': 'Mod347',
            'generate_ws_method': '_mod347_report',
            'title': 'Mod347',
            'wanted_list': wanted_list,
            'col_specs': mod347_template,
        }
        
        return [ws_params]

    def _mod347_report(self, workbook, ws, ws_params, data, mod347s):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])
        self._set_column_width(ws, ws_params)
        row_pos = 0
        if len(mod347s) == 1:
            ws_params['title'] = mod347s.name
            row_pos = self._write_ws_title(ws, row_pos, ws_params)
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='header',
                default_format=self.format_theader_yellow_left)
        ws.freeze_panes(row_pos, 0)
        wl = ws_params['wanted_list']

        for mod347 in mod347s:
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='data',
                render_space={
                    'mod347': mod347,
                },
                default_format=self.format_tcell_left)
