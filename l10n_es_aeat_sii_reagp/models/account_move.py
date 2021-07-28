# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

#     @api.multi
#     def _get_not_amount_taxes(self):
#         self.ensure_one()
#         not_amount_taxes = super(AccountMove, self)._get_not_amount_taxes()
#         taxes_sfrsreagp = self._get_taxes_map(['SFRSREAGP'])
#         for tax_line in self.tax_line_ids:
#             if tax_line.tax_id not in taxes_sfrsreagp:
#                 not_amount_taxes += tax_line.amount
#         print(not_amount_taxes)
#         return not_amount_taxes

    def _get_sii_tax_line(self, tax_line, line, line_taxes):
        self.ensure_one()
        tax_sii = super(AccountMove, self)._get_sii_tax_line(
            tax_line, line, line_taxes)
        taxes_sfrsreagp = self._get_taxes_map(['SFRSREAGP'])
        if tax_line in taxes_sfrsreagp:
            tax_sii['PorcentCompensacionREAGYP'] = tax_sii['TipoImpositivo']
            tax_sii['ImporteCompensacionREAGYP'] = tax_sii['CuotaSoportada']
        return tax_sii

    def _update_sii_tax_line(self, tax_sii, tax_line, line, line_taxes):
        self.ensure_one()
        taxes_sfrsreagp = self._get_taxes_map(['SFRSREAGP'])
        if tax_line in taxes_sfrsreagp:
            tax_type = tax_type = tax_line.amount
            taxes = tax_line.compute_all(
                price_unit=self._get_line_price_subtotal(line),
                quantity=line.quantity, product=line.product_id,
                partner=line.move_id.partner_id)
            tax_sii[str(tax_type)]['BaseImponible'] += taxes['total_excluded']
            tax_sii[str(tax_type)]['ImporteCompensacionREAGYP'] += \
                taxes['taxes'][0]['amount']
        else:
            tax_sii = super(AccountMove, self)._update_sii_tax_line(
                tax_sii, tax_line, line, line_taxes)
        return tax_sii

    def _get_invoices(self):
        self.ensure_one()
        invoices = super(AccountMove, self)._get_invoices()
        if self.move_type in ['in_invoice', 'in_refund']:
            lines = invoices['FacturaRecibida']['DesgloseFactura'][
                'DesgloseIVA']['DetalleIVA']
            invoices['FacturaRecibida']['DesgloseFactura'][
                'DesgloseIVA']['DetalleIVA'] = []
            cuota_deducible = 0.0
            for line in lines:
                if 'PorcentCompensacionREAGYP' in line:
                    line.pop('TipoImpositivo')
                    line.pop('CuotaSoportada')
                    line['ImporteCompensacionREAGYP'] = \
                        round(line['ImporteCompensacionREAGYP'], 2)
                    cuota_deducible += line['ImporteCompensacionREAGYP']
                else:
                    cuota_deducible += line['CuotaSoportada']
                invoices['FacturaRecibida']['DesgloseFactura'][
                    'DesgloseIVA']['DetalleIVA'].append(line)
                invoices['FacturaRecibida']['CuotaDeducible'] = cuota_deducible
        _logger.info(invoices)
        return invoices
