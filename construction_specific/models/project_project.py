from openerp import models, fields, api


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

    date_estimated = fields.Datetime(string="Fecha requerida",
                                     compute="_get_date_estimated")
    date_shipped = fields.Datetime(string="Fecha entregado",
                                   compute=_get_date_shipped)

class Task(models.Model):
    _inherit = 'project.task'

    project_state = fields.Selection(string='State', related='project_id.state')
