# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models


class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  default=False, required=True)


'''
class hr_timesheet_line(models.Model):
    _inherit = "hr.analytic.timesheet"

    def _default_date(self, cr, uid, context=None):
        if 'timesheet_date_from' in context:
            return context['timesheet_date_from']
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r=='month':
            return time.strftime('%Y-%m-01')
        elif r=='week':
            return (datetime.today() + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r=='year':
            return time.strftime('%Y-01-01')
        return (datetime.today() - relativedelta(days=1)).strftime('%Y-%m-%d')

    _defaults = {
        'date': _default_date,
        }
'''