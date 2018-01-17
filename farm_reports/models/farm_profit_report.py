# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
from openerp import tools


class FarmCostReport(models.Model):
    _name = 'farm.report.profit'
    _auto = False

    number = fields.Char(string='Group lot')
    date = fields.Date(string='Sale date', readonly=True)
    farm = fields.Many2one(string='farm', comodel_name='stock.location',
                           readonly=True)
    feed_qty = fields.Float(string='feed_quantity')
    profit_per_unit = fields.Float(string='profit per unit',
                                   group_operator = 'avg')
    profit = fields.Float(string='profit')
    weight = fields.Float(string='weight')
    profit_per_kg = fields.Float(string='profit per kg', digits=(10, 4),
                                 group_operator = 'avg')
    feed_cost = fields.Float(string='Feed cost', digits=(10, 4))
    other_cost = fields.Float(string='Other cost', digits=(10, 4))
    transition_cost = fields.Float(string='Transition cost', digits=(10, 4))
    total_cost = fields.Float(string='Total cost', digits=(10, 4))

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'farm_report_profit')
        cr.execute(
            """create or replace view farm_report_profit as (
            select id,number,date,farm,feed_qty,profit,profit_per_unit,weight,
            profit_per_kg,feed_cost,other_cost,transition_cost,total_cost from
            (select
            ag.id as id,
            ag.number as number,
            ag.removal_date as date,
            ag.farm as farm,
            feed_quantity as feed_qty,
            SUM(amount) as profit,
            (SUM(amount)/ag.initial_quantity) as profit_per_unit,
            (select SUM(weight) from farm_animal_group_weight
            where party = ag.id and weight/quantity > 20
            group by party)as weight,
            (SUM(amount)/(select SUM(weight)
            from farm_animal_group_weight where party = ag.id and
            weight/quantity > 20 group by party)) as profit_per_kg
            from farm_animal_group as ag
            inner join account_analytic_account as aaa
            on ag.account = aaa.id inner join account_analytic_line as aal
            on aaa.id = aal.account_id
            where (ag.state='fatten' and removal_date is not
            null) or ag.state='sold'
            group by ag.id order by removal_date)as q1
            left join
            (select
            ag.id as id2,
            SUM(amount) as feed_cost
            from farm_animal_group as ag
            inner join account_analytic_account as aaa
            on ag.account = aaa.id inner join account_analytic_line as aal
            on aaa.id = aal.account_id
            where ((aal.name like 'mrp-cost%' or aal.ref='feed')and
            aal.date > ag.fatten_date) and ((ag.state='fatten' and
            removal_date is not null) or ag.state='sold')
            group by ag.id order by removal_date)as q2 on q1.id = q2.id2
            left join
            (select
            ag.id as id3,
            SUM(amount) as other_cost
            from farm_animal_group as ag
            inner join account_analytic_account as aaa
            on ag.account = aaa.id inner join account_analytic_line as aal
            on aaa.id = aal.account_id
            where ((aal.name not like 'mrp-cost%' and aal.ref is Null
            and aal.name!='sale') and aal.date > ag.fatten_date) and
            ((ag.state='fatten' and removal_date is not null) or
            ag.state='sold')
            group by ag.id order by removal_date)as q3 on q1.id = q3.id3
            left join
            (select
            ag.id as id4,
            SUM(amount) as transition_cost
            from farm_animal_group as ag
            inner join account_analytic_account as aaa
            on ag.account = aaa.id inner join account_analytic_line as aal
            on aaa.id = aal.account_id
            where (aal.name!='sale' and aal.date <= ag.fatten_date) and
            ((ag.state='fatten' and removal_date is not
            null) or ag.state='sold')
            group by ag.id order by removal_date)as q4 on q1.id = q4.id4
            left join
            (select
            ag.id as id5,
            SUM(amount) as total_cost
            from farm_animal_group as ag
            inner join account_analytic_account as aaa
            on ag.account = aaa.id inner join account_analytic_line as aal
            on aaa.id = aal.account_id
            where aal.name!='sale' and ((ag.state='fatten' and
             removal_date is not
            null) or ag.state='sold')
            group by ag.id order by removal_date)as q5 on q1.id = q5.id5)
            """)
