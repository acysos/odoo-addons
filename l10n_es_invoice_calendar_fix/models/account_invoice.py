# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2017  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        invoice_date = vals.get('date_invoice')
        if invoice_date and self.state != 'draft':
            raise Warning(_('The invoice date can only be modified in draft '
                            'status, update the browser to see the dates again'
                            ' correctly or press Crt + F5'))
        res = super(AccountInvoice, self).write(vals)
        return res
