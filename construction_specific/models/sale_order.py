# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('order_line')
    def _get_total_human(self):
        for order in self:
            order.total_human = 0
            for line in order.order_line:
                self.total_human += line.line_human

    @api.multi
    @api.onchange('order_line')
    def _get_total_material(self):
        for order in self:
            order.total_material = 0
            for line in order.order_line:
                self.total_material += line.line_material

    @api.multi
    @api.onchange('total_human', 'total_material')
    def _get_total_cost(self):
        for order in self:
            order.sale_costs = 0
            order.sale_costs += order.total_human * \
                self.env.user.company_id.human_cost + order.total_material

    @api.multi
    def button_calculate_totals(self):
        for order in self:
            order._get_total_cost()
            order._get_total_human()
            order._get_total_material()
            order._get_bi()
            order._get_per_bi()

    @api.multi
    @api.onchange('amount_untaxed')
    def _get_bi(self):
        for order in self:
            order.industrial_profit = order.amount_untaxed - order.sale_costs

    @api.multi
    @api.onchange('amount_untaxed')
    def _get_per_bi(self):
        for order in self:
            if order.amount_untaxed != 0:
                order.percentage_ip = (order.industrial_profit /
                                       order.amount_untaxed) * 100
            else:
                order.percentage_ip = 0

    '''
    @api.multi
    def _get_project_state(self):
        for sale in self:
            state = _('Finised')
            if len(sale.related_project_id.tasks) > 0:
                for task in sale.project_id.tasks:
                    if task.stage_id.id != 7:
                        state = _('Process')
            else:
                state = ''
            sale.project_state = state
    '''

    @api.model
    def _prepare_project_vals(self, order):
        vals = super(SaleOrder, self)._prepare_project_vals(order)
        vals['name'] = u" %s - %s" % (
            order.name,
            order.partner_id.comercial)
        return vals

    @api.multi
    def _get_date_shipped(self):
        for order in self:
            date = None
            for picking in order.picking_ids:
                if date is None or date < picking.date_done:
                    date = picking.date_done
            order.date_shipped = date

    @api.multi
    def _amount_all_wrapper(self):
        """
        Wrapper because of direct method passing as parameter
        for function fields """
        for res in self:
            bi = res.amount_untaxed - res.sale_costs
            if res.amount_untaxed != 0:
                per_bi = (bi/res.amount_untaxed)*100
            else:
                per_bi = 0
            res.industrial_profit = bi
            res.percentage_ip = per_bi

    @api.multi
    def _get_balance(self):
        for order in self:
            if order.project_id:
                order.analytic_balance = \
                    order.project_id.balance
            else:
                order.analytic_balance = 0

    industrial_profit = fields.Float(
        compute=_amount_all_wrapper,
        digits_compute=dp.get_precision('Account'), string='BI',
        multi='sums', help="Industrial profit", track_visibility='always')
    percentage_ip = fields.Float(
        compute=_amount_all_wrapper,
        digits_compute=dp.get_precision('Account'), string='% BI',
        multi='sums', help="Industrial profit percent",
        track_visibility='always')
    order_line = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id', string='Order Lines', copy=True)
    sale_costs = fields.Float(string='Total cost')
    total_human = fields.Float(string='Total work force')
    total_material = fields.Float(string='Total Materials')
    date_estimated = fields.Datetime(string="Estimated date")
    date_shipped = fields.Datetime(string="Shiped date",
                                   compute=_get_date_shipped)
    analytic_balance = fields.Float(
        string='Coste/Beneficio',
        compute=_get_balance)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('line_human', 'line_material')
    def _get_line_cost(self):
        for line in self:
            line.line_costs = line.line_human * \
                self.env.user.company_id.human_cost + line.line_material

    line_human = fields.Float(string='work feorce')
    line_material = fields.Float(string='Materals')
    line_costs = fields.Float(string='Cost')
