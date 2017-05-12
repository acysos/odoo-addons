# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
from openerp import tools


class FarmAccountSalesReport(models.Model):
    _name = 'farm.report.account.sales'
    _auto = False

    sale_order_id = fields.Many2one(string='Account',
                                    comodel_name='account.account',
                                    readonly=True)
    period_id = fields.Many2one(string='Period', comodel_name='account.period',
                                readonly=True)
    amount_total = fields.Float(string='total', readonly=True)
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product', readonly=True)
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner',
                                 readonly=True)
    weight = fields.Float(string='Weight', readonly=True)
    animal_qty = fields.Integer(string='num. of animals', readonly=True)
    farm = fields.Many2one(string='farm', comodel_name='stock.warehouse',
                           readonly=True)
    month = fields.Selection(string='month', selection=[
                            ('01', 'January'), ('02', 'February'),
                            ('03', 'March'), ('04', 'April'), ('05', 'May'),
                            ('06', 'June'), ('07', 'July'), ('08', 'August'),
                            ('09', 'September'), ('10', 'October'),
                            ('11', 'November'), ('12', 'December')],
                             readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_account_sales')
        cr.execute("""create or replace view farm_report_account_sales as (
            select
               min(inv_line.id) as id,
               to_char(inv.date_invoice,'MM') as month,
               sum(inv_line.price_subtotal) as amount_total,
               inv.period_id,
               inv_line.product_id,
               sum(inv_line.quantity) as weight,
               sal_or.id as sale_order_id,
               sum(inv_line.animal_qty) as animal_qty,
               warehouse_id as farm,
               sal_or.partner_id
               
            from
                sale_order sal_or
            inner join sale_order_invoice_rel sa_in_rel 
                on sal_or.id = sa_in_rel.order_id 
            inner join account_invoice inv on inv.id = sa_in_rel.invoice_id 
            inner join account_invoice_line inv_line on inv.id = inv_line.invoice_id
            inner join account_account account on account.id = inv_line.account_id
            where
                inv.state in ('open','paid')
            group by
                to_char(inv.date_invoice, 'YYYY'),to_char(inv.date_invoice,'MM'), inv.period_id, inv_line.product_id, sal_or.id
            )""")
