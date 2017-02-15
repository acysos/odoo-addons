from openerp import models


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'
    _order = 'date desc'
