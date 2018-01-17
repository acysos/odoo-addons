# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
from openerp import tools


class LotCostReport(models.Model):
    _name = 'mrp.lot.cost.report'
    _auto = False

    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product', readonly=True)
    lot_cost = fields.Float(string='Lot Cost', digits=(10, 4),
                            group_operator = 'avg')
    dates = fields.Date(string='Date')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'mrp_lot_cost_report')
        cr.execute("""create or replace view mrp_lot_cost_report as (
            select
                min(mrp.id) as id,
                lot.product_id as product_id,
                lot.create_date::timestamp::date as dates,
                avg(lot.unit_cost) as lot_cost
            from
                mrp_production mrp
            inner join stock_move move
                on mrp.id = move.production_id
            inner join stock_quant_move_rel qmrel
                on move.id = qmrel.move_id
            inner join stock_quant quant
                on qmrel.quant_id = quant.id
            inner join stock_production_lot lot
                on quant.lot_id = lot.id
            group by lot.product_id, dates
            order by dates)
            """)
