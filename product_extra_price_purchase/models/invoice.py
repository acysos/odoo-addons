# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Alexander Ezquebo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def expand_extra_prices(self):
        updated_invoices = []
        inv_line_obj = self.env['account.invoice.line']
        fiscalp_obj = self.env['account.fiscal.position']
        for invoice in self:
            if invoice.type in ['out_invoice', 'out_refund']:
                super(AccountInvoice, self).expand_extra_prices()
            else:
                fiscal_position = invoice.fiscal_position and \
                    fiscalp_obj.browse(invoice.fiscal_position.id) or False
                sequence = -1
                reorder = []
                for line in invoice.invoice_line:
                    sequence += 1
                    if sequence > line.sequence:
                        line.sequence = sequence
                    else:
                        sequence = line.sequence
                    if not line.product_id:
                        continue
                    if line.product_id.extra_price_purchase == 0:
                        continue
                    if line.extra_child_line_id:
                        continue
                    sequence += 1
                    tax_ids = fiscal_position.map_tax(
                        line.product_id.product_id_extra.taxes_id)
                    vals = self.prepare_extra_invoice_vals(
                        line, sequence, tax_ids)
                    extra_line = inv_line_obj.create(vals)
                    if invoice.id not in updated_invoices:
                        updated_invoices.append(invoice.id)
                    line.extra_child_line_id = extra_line.id
                    line.total_extra_price = extra_line.price_subtotal
                    if invoice.company_id.price_extra_included_purchase:
                        extra_line.unlink()
                    for line_id in reorder:
                        line_id.sequence = sequence
                        sequence += 1

            account_invoice_tax = self.env['account.invoice.tax']
            ctx = dict(self._context)
            for invoice in self:
                self._cr.execute(
                    "DELETE FROM account_invoice_tax WHERE invoice_id"
                    "=%s AND manual is False", (invoice.id,))
                self.invalidate_cache()
                partner = invoice.partner_id
                if partner.lang:
                    ctx['lang'] = partner.lang
                for taxe in account_invoice_tax.compute(
                        invoice.with_context(ctx)).values():
                    account_invoice_tax.create(taxe)
