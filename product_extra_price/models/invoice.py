# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Alexander Ezquebo <alexander@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    extra_parent_line_id = fields.Many2one(
        comodel_name='account.invoice.line', string='Extra Price',
        help='The line that contain the product with the extra price')
    extra_child_line_id = fields.Many2one(
        comodel_name='account.invoice.line', string='Line extra price',
        help='', copy=False)
    sequence = fields.Integer(
        string='Sequence', default=100,
        help="Gives the sequence order when displaying a list of invoice "
        "lines.")
    total_extra_price = fields.Float(string="Total extra price",
                                     digits=dp.get_precision('Account'))

    _order = 'sequence, id desc'


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _get_total_extra(self):
        for invoice in self:
            for line in invoice.invoice_line:
                invoice.total_extra_price += line.total_extra_price

    total_extra_price = fields.Float(
        string="Total extra price",
        digits=dp.get_precision('Account'),
        compute=_get_total_extra)

    @api.one
    def copy(self, default=None):
        res = super(AccountInvoice, self).copy(default)
        for line in res.invoice_line:
            if line.extra_parent_line_id:
                line_in = self.env['account.invoice.line'].search(
                    [('extra_child_line_id', '=', line.id),
                     ('invoice_id', '=', res.id)])
                if not line_in:
                    line.unlink()
        return res

    @api.model
    def create(self, vals):
        result = super(AccountInvoice, self).create(vals)
        result.expand_extra_prices()
        return result

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        self.expand_extra_prices()
        return res

    def prepare_extra_invoice_vals(self, line, sequence, tax_ids):
        dis_policy = line.product_id.discount_policy
        if dis_policy == 'same':
            discount = line.discount
        elif dis_policy == 'only' and line.discount == 100.00:
            discount = 100.00
        else:
            discount = 0
        if line.product_id.extra_price != 0:
            price_unit = line.product_id.extra_price
        else:
            price_unit = line.product_id.product_id_extra.list_price
        vals = {'name': '-- '+(line.product_id.name_extra_price or ''),
                'origin': line.origin,
                'invoice_id': line.invoice_id.id,
                'uos_id': line.uos_id.id,
                'account_id': line.account_id.id,
                'price_unit': price_unit,
                'quantity': line.quantity,
                'discount': discount,
                'invoice_line_tax_id': tax_ids,
                'account_analytic_id': line.account_analytic_id.id or None,
                'company_id': line.company_id.id,
                'partner_id': line.partner_id.id,
                'extra_parent_line_id': line.id,
                'sequence': sequence,
                'product_id': line.product_id.product_id_extra.id or None,
                }
        return vals

    def expand_extra_prices(self):
        updated_invoices = []
        inv_line_obj = self.env['account.invoice.line']
        fiscalp_obj = self.env['account.fiscal.position']
        for invoice in self:
            fiscal_position = invoice.fiscal_position and fiscalp_obj.browse(
                    invoice.fiscal_position.id) or False
            sequence = -1
            reorder = []
            if invoice.type not in ['out_invoice', 'out_refund']:
                continue
            for line in invoice.invoice_line:
                sequence += 1
                if sequence > line.sequence:
                    line.sequence = sequence
                else:
                    sequence = line.sequence
                if not line.product_id:
                    continue
                if line.product_id.extra_price == 0:
                    continue
                if line.extra_child_line_id:
                    continue
                sequence += 1
                tax_ids = fiscal_position.map_tax(
                    line.product_id.product_id_extra.taxes_id)
                vals = self.prepare_extra_invoice_vals(line, sequence, tax_ids)
                extra_line = inv_line_obj.create(vals)
                if invoice.id not in updated_invoices:
                    updated_invoices.append(invoice.id)
                line.extra_child_line_id = extra_line.id
                line.total_extra_price = extra_line.price_subtotal
                if invoice.company_id.price_extra_included_sale:
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

    def _refund_cleanup_lines(self, lines):
        lines2 = []
        for line in lines:
            if 'extra_parent_line_id' in line and \
                    'extra_child_line_id' in line:
                if not line['extra_parent_line_id'] and not line[
                        'extra_child_line_id']:
                    lines2.append(line)
            else:
                lines2.append(line)

        for line in lines2:
            del line['id']
            del line['invoice_id']
            for field in ('company_id', 'partner_id', 'account_id',
                          'product_id', 'uos_id', 'account_analytic_id',
                          'tax_code_id', 'base_code_id'):
                line[field] = line.get(field, False) and line[field][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = [(6, 0, line.get(
                    'invoice_line_tax_id', []))]
        return map(lambda x: (0, 0, x), lines2)
