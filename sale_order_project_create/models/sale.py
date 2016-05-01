# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def create_project(self, order):
        project = False
        for line in order.order_line:
            prod = line.product_id
            if prod.auto_create_task and len(prod.project_id) == 0:
                project = True
        if project and not order.related_project_id:
            project_obj = self.env['project.project']
            vals = self._prepare_project_vals(order)
            project = project_obj.create(vals)
            order.project_id = project.analytic_account_id.id
        return True

    @api.multi
    def action_button_confirm(self):
        for order in self:
            self.create_project(order)
        return super(SaleOrder, self).action_button_confirm()
