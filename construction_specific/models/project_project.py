# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    @api.multi
    def _get_date_estimated(self):
        sale_obj = self.env['sale.order']
        for project in self:
            sale = sale_obj.search([('project_id', '=', project.id)])
            date_est = None
            for order in sale:
                if order.date_estimated > date_est or date_est is None:
                    date_est = order.date_estimated
            project.date_estimated = date_est

    @api.multi
    def _get_date_shipped(self):
        sale_obj = self.env['sale.order']
        for project in self:
            sale = sale_obj.search([('project_id', '=', project.id)])
            date_shipped = None
            for order in sale:
                if order.date_shipped > date_shipped or date_shipped is None:
                    date_shipped = order.date_shipped
            project.date_shipped = date_shipped

    date_estimated = fields.Datetime(string="Estimated day",
                                     compute="_get_date_estimated")
    date_shipped = fields.Datetime(string="Shipped day",
                                   compute=_get_date_shipped)

class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _get_project_state(self):
        for task in self:
            if task.project_id:
                task.project_state = task.project_id.state

    project_state = fields.Char(string='State', compute=_get_project_state)
