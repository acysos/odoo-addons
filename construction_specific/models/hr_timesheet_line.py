from openerp import models, api


class hr_timesheet_line(models.Model):
    _inherit = "hr.analytic.timesheet"

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if vals['name'] == '/':
            vals['name'] = self.env['project.task'].browse(
                vals['task_id']).name
        return models.Model.create(self, vals)

    @api.onchange('account_id', 'task_id')
    def _change_name(self):
        name = ''
        if self.account_id:
            name += self.account_id.name
        if self.task_id:
            name += ' - ' + self.task_id.name
        self.name = name
