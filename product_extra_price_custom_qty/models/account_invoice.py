# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2017  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def prepare_extra_invoice_vals(self, line, sequence, tax_ids):
        vals = super(AccountInvoice, self).prepare_extra_invoice_vals(
            line, sequence, tax_ids)
        qty = line.product_id.extra_price_qty * line.quantity
        vals['quantity'] = qty
        return vals
