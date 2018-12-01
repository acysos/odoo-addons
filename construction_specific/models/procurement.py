# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class procurement_order(models.Model):
    _inherit = "procurement.order"

#     @api.multi
#     def _is_procurement_task(self):
#         for res in self:
#             is_proc_task = super(procurement_order, self)._is_procurement_task()
#             if res.product_id.type == 'consu' and \
#                     res.product_id.auto_create_task:
#                 is_proc_task = True
#         return is_proc_task
    
    @api.multi
    def _convert_qty_company_hours(self):
        for res in self:
            product_uom = self.env['product.uom']
            company_time_uom_id = self.user.company_id.project_time_mode_id
            if res.product_uom.id != company_time_uom_id.id and \
                    res.product_uom.category_id.id == company_time_uom_id.category_id.id:
                planned_hours = product_uom._compute_qty(
                    res.product_uom.id, res.sale_line_id.line_human,
                    company_time_uom_id.id)
            else:
                planned_hours = res.sale_line_id.line_human
        return planned_hours
