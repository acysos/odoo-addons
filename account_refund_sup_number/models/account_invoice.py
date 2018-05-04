# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _prepare_refund(
            self, invoice, date=None, period_id=None, description=None,
            journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date, period_id, description, journal_id)
        if 'supplier_invoice_number' in self.env.context:
            values['supplier_invoice_number'] = self.env.context[
                'supplier_invoice_number']
        return values
