# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _create_service_task(self, procurement):
        project_task = self.env['project.task']
        project = self._get_project(procurement)
        task_id = None
        if project and not procurement.task_id:
            task = project_task.search([('project_id', '=', project.id)])
            if task:
                if not procurement.sale_line_id.task_count:
                    planned_hours = self._convert_qty_company_hours(
                        procurement)
                    task.planned_hours += planned_hours
                    task.remaining_hours += planned_hours
                    task.sale_line_id = procurement.sale_line_id
                    task_id = task.id
                    procurement.task_id = task_id
                    procurement.sale_line_id.task_count = True
            else:
                task_id = super(ProcurementOrder,
                                self)._create_service_task(procurement)
                task = project_task.browse(task_id)
                task.name = task.sale_line_id.order_id.task_name
                procurement.sale_line_id.task_count = True

        return task_id
