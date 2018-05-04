# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.multi
    def _get_inv_type(self):
        return self._context.get('type', 'out_invoice')

    invoice_type = fields.Char(string='Original invoice type',
                               default=_get_inv_type)
    sup_invoice_number = fields.Char(string='Supplier invoice number')

    @api.multi
    def compute_refund(self, mode='refund'):
        context = self._context.copy()
        context['supplier_invoice_number'] = self.sup_invoice_number
        self = self.with_context(context)
        result = super(AccountInvoiceRefund, self).compute_refund(mode)
        return result
