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
            if self.amount_total > 400:
                raise UserError(_(
                    "The total of the invoice %s is more that 400 €") % (
                        self.invoice_number))
            if self.amount_total < 0 or self.type in ['in_refund', 'out_refund']:
                tipo_factura = 'R5'
            else:
                tipo_factura = 'F2'
            return tipo_factura
        return tipo_factura

    @api.multi
    def _get_invoices(self):
        self.ensure_one()
        if self.simplified_invoice and not self.partner_id.vat:
            self.partner_id.vat = 'ESA12345674'
        return super(AccountInvoice, self)._get_invoices()
