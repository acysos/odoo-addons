# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2016  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_payment_lines(self):
        line_obj = self.env['account.move.line']
        for invoice in self:
            if invoice.id:
                payment_lines = line_obj.search([('invoice', '=', invoice.id),
                                                 ('date_maturity', '!=', None)],
                                                order='date_maturity asc')
                payment_line_ids = []
                for line in payment_lines:
                    payment_line_ids.append(line.id)
                invoice.payment_lines = payment_line_ids
    
    payment_lines = fields.Many2many(string='Payment Terms',
                                     comodel_name='account.move.line',
                                     compute='_get_payment_lines')
