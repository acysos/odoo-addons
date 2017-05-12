# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api


DIST_TYPE = [('unit', 'PER UNIT'), ('by_delivery', 'PER DELIVERY'),
             ('total', 'TOTAL')]


class LandedCostTemplate(models.Model):
    _name = 'purchase.landedcost.template'

    name = fields.Char(string='name')
    provider = fields.Many2one(string='Transport company',
                               comodel_name='res.partner',
                               domain=[('supplier', '=', True)])
    type = fields.Selection(string='Cost distribution',
                            selection=DIST_TYPE, default='total')
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='price')


class LandedCost(models.Model):
    _name = 'purchase.landedcost'
    _inherit = {'purchase.landedcost.template': 'landed_cost_template_id'}
    _rec_name = 'provider'

    template_id = fields.Many2one(string='Template',
                                  comodel_name='purchase.landedcost.template')
    invoice_id = fields.Many2one(string='Invoice',
                                 comodel_name='account.invoice')
    purchase_id = fields.Many2one(string='Purchase',
                                  comodel_name='purchase.order',
                                  inverse_name='landed_cost_id')

    @api.onchange('template_id')
    @api.multi
    def on_change_template(self):
        for res in self:
            if res.template_id:
                res.provider = res.template_id.provider
                res.type = res.template_id.type
                res.quantity = res.template_id.quantity
                res.price = res.template_id.price

    @api.multi
    def set_total_cost(self, lines):
        for res in self:
            if res.type == 'unit':
                cost_p_u = (res.price/res.quantity)
            elif res.type == 'total':
                total = 0
                for line in lines:
                    total = total + line.product_qty
                cost_p_u = res.price/total
            else:
                total_units = 0
                total_deliv = len(res.purchase_id.picking_ids)
                total_cost = total_deliv * res.price
                for line in lines:
                    total_units = total_units + line.product_qty
                cost_p_u = total_cost/total_units
            for line2 in lines:
                line2.total_cost = line2.price_unit + cost_p_u
