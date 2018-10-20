# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    discount = fields.Float(string='Calculated discount', digits=(10, 2))
    discount1 = fields.Float(string='Discount 1', digits=(10, 2))
    discount2 = fields.Float(string='Discount 2', digits=(10, 2))
    discount3 = fields.Float(string='Discount 3', digits=(10, 2))
    
    @api.onchange('discount1', 'discount2', 'discount3')
    def _calculate_discount(self):
        if self.invoice_id.type in ['in_invoice', 'in_refund']:
            self.discount = 100 * (1 - ((100 - self.discount1) / 100.00 * (
                100 - self.discount2) / 100 * (100 - self.discount3) / 100.00))
        
    @api.multi
    def write(self, vals):
        for line in self:
            if line.invoice_id.type in ['in_invoice', 'in_refund']:
                if 'discount1' in vals:
                    discount1 = vals['discount1']
                else:
                    discount1 = line.discount1
                if 'discount2' in vals:
                    discount2 = vals['discount2']
                else:
                    discount2 = line.discount2
                if 'discount3' in vals:
                    discount3 = vals['discount3']
                else:
                    discount3 = line.discount3
            res = super(account_invoice_line, self).write(vals)

    
    @api.model
    def create(self, vals):
        if 'invoice_id' in vals:
            invoice = self.invoice_id.search([('id', '=', vals['invoice_id'])])
            type = invoice.type
        else:
            type = False
        if type in ['in_invoice', 'in_refund'] or 'discount1' in vals:
            if 'discount1' in vals:
                discount1 = vals['discount1']
            else:
                discount1 = 0
            if 'discount2' in vals:
                discount2 = vals['discount2']
            else:
                discount2 = 0
            if 'discount3' in vals:
                discount3 = vals['discount3']
            else:
                discount3 = 0
            vals['discount'] = 100 * (1 - ((100 - discount1) / 100.00 * (
                100 - discount2) / 100.00 * (100 - discount3) / 100.00))
        res = super(account_invoice_line, self).create(vals)
        return res
