# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_sii_tax_line(self, tax_line, line, line_taxes):
        self.ensure_one()
        tax_sii = super(AccountInvoice, self)._get_sii_tax_line(
            tax_line, line, line_taxes)
        taxes_sfrsreagp = self._get_taxes_map(['SFRSREAGP'])
        if tax_line in taxes_sfrsreagp:
            tax_sii['PorcentCompensacionREAGYP'] = tax_sii['TipoImpositivo']
            tax_sii['ImporteCompensacionREAGYP'] = tax_sii['CuotaSoportada']
        return tax_sii

    @api.multi
    def _update_sii_tax_line(self, tax_sii, tax_line, line, line_taxes):
        self.ensure_one()
        taxes_sfrsreagp = self._get_taxes_map(['SFRSREAGP'])
        if tax_line in taxes_sfrsreagp:
            tax_type = tax_type = tax_line.amount * 100
            taxes = tax_line.compute_all(
                price_unit=self._get_line_price_subtotal(line),
                quantity=line.quantity, product=line.product_id,
                partner=line.invoice_id.partner_id)
            tax_sii[str(tax_type)]['BaseImponible'] += taxes['total_excluded']
            tax_sii[str(tax_type)]['ImporteCompensacionREAGYP'] += \
                taxes['taxes'][0]['amount']
        else:
            tax_sii = super(AccountInvoice, self)._update_sii_tax_line(
                tax_sii, tax_line, line, line_taxes)
        return tax_sii

    @api.multi
    def _get_invoices(self):
        self.ensure_one()
        invoices = super(AccountInvoice, self)._get_invoices()
        if self.type in ['in_invoice', 'in_refund']:
            lines = invoices['FacturaRecibida']['DesgloseFactura'][
                'DesgloseIVA']['DetalleIVA']
            invoices['FacturaRecibida']['DesgloseFactura'][
                'DesgloseIVA']['DetalleIVA'] = []
            for line in lines:
                if 'PorcentCompensacionREAGYP' in line:
                    line.pop('TipoImpositivo')
                    line.pop('CuotaSoportada')
                    line['ImporteCompensacionREAGYP'] = \
                        round(line['ImporteCompensacionREAGYP'], 2)
                invoices['FacturaRecibida']['DesgloseFactura'][
                    'DesgloseIVA']['DetalleIVA'].append(line)
        return invoices

