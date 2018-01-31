# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, api, fields


class SaleCommission(models.Model):
    _inherit = 'sale.commission'

    commission_type = fields.Selection(
        selection_add=[("variable", "Variable")])
    condition_ids = fields.One2many(string="Conditions",
                                    comodel_name='sale.commission.condition',
                                    inverse_name='commission_id')

    @api.multi
    def calculate_conditions(self, sale_line):
        self.ensure_one()
        for condition in self.condition_ids:
            if condition.check_condition(sale_line):
                return condition.get_conditional_com(sale_line)
        for condition in self.condition_ids:
            if condition.default_commission:
                return condition.get_conditional_com(sale_line)
        return 0.0


class SaleCommissionCondition(models.Model):
    _name = "sale.commission.condition"

    name = fields.Char('Name', required=True)
    commission_id = fields.Many2one(string='Parent_commission',
                                   comodel_name='sale.commission')
    commission_type = fields.Selection(
        selection=[("fixed", "Fixed percentage"),
                   ("section", "By sections")],
        string="Type", required=True, default="fixed")
    partner_ids = fields.Many2many(
        string='Customers', comodel_name='res.partner',
        domain=[('customer', '=', True)])
    product_ids = fields.Many2many(
        string='Products', comodel_name='product.product')
    default_commission = fields.Boolean(string='Default Section')
    fix_qty = fields.Float(string="Fixed percentage")
    sections = fields.One2many(
        comodel_name="sale.commission.section", inverse_name="commission")
    amount_base_type = fields.Selection(
        selection=[('gross_amount', 'Gross Amount'),
                   ('net_amount', 'Net Amount')],
        string='Base', required=True, default='gross_amount')

    @api.multi
    def check_condition(self, sale_line):
        for sec in self:
            control = False
            if sec.partner_ids:
                if sale_line.order_partner_id in sec.partner_ids:
                    control = True
                else:
                    return False
            if sec.product_ids:
                if sale_line.product_id in sec.product_ids:
                    control = True
                else:
                    return False
            return control

    @api.multi
    def get_conditional_com(self, sale_line):
        for condition in self:
            amount = 0.0
            subtotal = sale_line.tax_id.compute_all(
                (sale_line.price_unit *
                 (1 - (sale_line.discount or 0.0) / 100.0)),
                sale_line.product_uom_qty, sale_line.product_id,
                sale_line.order_id.partner_id)
            if condition.amount_base_type == 'net_amount':
                subtotal = subtotal['total_included']
            else:
                subtotal = subtotal['total']
            if condition.commission_type == 'fixed':
                amount = subtotal * (condition.fix_qty / 100.0)
            else:
                amount = condition.calculate_section(subtotal)
            return amount

    @api.multi
    def calculate_section(self, base):
        self.ensure_one()
        for section in self.sections:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0
        return 0.0


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends('sale_line.price_subtotal')
    def _compute_amount(self):
        for res in self:
            if (res.commission.commission_type == 'variable' and
                not res.sale_line.product_id.commission_free and
                    res.commission):
                l = res.sale_line
                res.amount = res.commission.calculate_conditions(l)
            else:
                super(SaleOrderLineAgent, res)._compute_amount()
