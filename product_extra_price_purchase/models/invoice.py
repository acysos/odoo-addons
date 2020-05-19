# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Alexander Ezquebo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def prepare_extra_invoice_vals(self, line, sequence, tax_ids):
        vals = super(AccountInvoice, self).prepare_extra_invoice_vals(
            line, sequence, tax_ids)
        if line.invoice_id.type in ['in_invoice', 'in_refund']:
            if line.product_id.extra_price_purchase:
                vals['price_unit'] = line.product_id.extra_price_purchase
            else:
                vals['price_unit'] = \
                    line.product_id.product_id_extra.standard_price
        return vals

    def expand_extra_prices(self):
        updated_invoices = []
        inv_line_obj = self.env['account.invoice.line']
        fiscalp_obj = self.env['account.fiscal.position']
        has_extra = False
        for invoice in self:
            if invoice.type in ['out_invoice', 'out_refund']:
                super(AccountInvoice, self).expand_extra_prices()
            else:
                fiscal_position = invoice.fiscal_position_id and \
                    fiscalp_obj.browse(invoice.fiscal_position_id.id) or False
                sequence = -1
                reorder = []
                for line in invoice.invoice_line_ids:
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
                    has_extra = True
            if has_extra:
#                 account_invoice_tax = self.env['account.invoice.tax']
#                 ctx = dict(self._context)
#                 self._cr.execute(
#                     "DELETE FROM account_invoice_tax WHERE invoice_id"
#                     "=%s AND manual is False", (invoice.id,))
#                 self.invalidate_cache()
#                 partner = invoice.partner_id
#                 if partner.lang:
#                     ctx['lang'] = partner.lang
#                 for taxe in account_invoice_tax.compute(
#                         invoice.with_context(ctx)).values():
#                     account_invoice_tax.create(taxe)
                invoice.compute_taxes()


    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        extra_found = False
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped(
                'purchase_line_id'):
            if line.product_id.product_id_extra or \
                    line.product_id.extra_price != 0:
                extra_found = True
        if not extra_found:
            return super(AccountInvoice, self).purchase_order_change()
        else:
            if not self.partner_id:
                self.partner_id = self.purchase_id.partner_id.id
    
            new_lines = self.env['account.invoice.line']
            for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
                if not line.extra_parent_line_id:
                    data = self._prepare_invoice_line_from_po_line(line)
                    new_line = new_lines.new(data)
                    new_line._set_additional_fields(self)
                    new_lines += new_line
    
            self.invoice_line_ids += new_lines
            self.payment_term_id = self.purchase_id.payment_term_id
            self.env.context = dict(self.env.context, from_purchase_order_change=True)
            self.purchase_id = False
            return {}
