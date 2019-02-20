# -*- coding: utf-8 -*-
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('simplified_invoice')
    def _simplified_invoice_change(self):
        for invoice in self:
            if invoice.simplified_invoice:
                invoice.journal_id = invoice.company_id.simplified_journal_id
            else:
                invoice.journal_id = False

    simplified_invoice = fields.Boolean(string='Simplified Invoice')

    @api.multi
    def _get_tipo_factura(self):
        self.ensure_one()
        tipo_factura = super(AccountInvoice, self)._get_tipo_factura()
        if self.simplified_invoice:
            if self.amount_total > self.company_id.simplified_limit:
                raise UserError(_(
                    "The total of the invoice %s is more that %f €") % (
                        self.invoice_number, self.company_id.simplified_limit))
            if self.amount_total < 0 or self.type in ['in_refund', 'out_refund']:
                tipo_factura = 'R5'
            else:
                tipo_factura = 'F2'
            return tipo_factura
        return tipo_factura

    @api.multi
    def _check_partner_vat(self):
        for invoice in self:
            if not invoice.simplified_invoice:
                super(AccountInvoice, self)._check_partner_vat()

    @api.multi
    def _get_sii_identifier(self):
        self.ensure_one()
        if self.simplified_invoice and not self.partner_id.vat:
            return {}
        else:
            return super(AccountInvoice, self)._get_sii_identifier()

    @api.multi
    def _get_invoices(self):
        self.ensure_one()
        invoices = super(AccountInvoice, self)._get_invoices()
        if self.simplified_invoice:
            if not 'NIF' in invoices['FacturaExpedida']['Contraparte']:
                invoices['FacturaExpedida'].pop('Contraparte', None)
        return invoices
        
        
        
        

