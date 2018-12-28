# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _get_supplier(self):
        pur_line_obj = self.env['purchase.order.line']
        for line in self:
            pur_line = pur_line_obj.search([('analytic_line', '=', line.id)])
            line.supplier = pur_line.partner_id.id

    @api.multi
    def _get_supplier_ref(self):
        pur_line_obj = self.env['purchase.order.line']
        for line in self:
            pur_line = pur_line_obj.search([('analytic_line', '=', line.id)])
            line.supplier_ref = pur_line.order_id.partner_ref

    supplier = fields.Many2one(string="supplier", comodel_name='res.partner',
                               compute='_get_supplier')
    supplier_ref = fields.Char(string="Ref. supplier", 
                               compute='_get_supplier_ref')
