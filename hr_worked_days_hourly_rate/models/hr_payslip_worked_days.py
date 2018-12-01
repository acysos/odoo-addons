# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import api, fields, models, _
from datetime import datetime
#from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_payslip_worked_days(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.multi
    def _get_total(self, field_name, arg=None):
        res = {}
        for wd in self:
            wd.total = wd.number_of_hours \
                * wd.hourly_rate * wd.rate / 100

    hourly_rate = fields.Float('Hourly Rate', help="""\
The employee's standard hourly rate for one hour of work.
Example, 25 Euros per hour.""", default=0)
    
    rate = fields.Float('Rate (%)', help="""\
The rate by which to multiply the standard hourly rate.
Example, an overtime hour could be paid the standard rate multiplied by 150%.
""", default=100)

        # When a worked day has a number of hours and an hourly rate,
        # it is necessary to have a date interval,
        # because hourly rates are likely to change over the time.
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    total = fields.Float(compute='_get_total', method=True, string="Total")
    
#     _defaults = {
#         'hourly_rate': 0,
#         'rate': 100,
#         'date_from': lambda *a: datetime.now().strftime(
#             DEFAULT_SERVER_DATE_FORMAT),
#         'date_to': lambda *a: datetime.now().strftime(
#             DEFAULT_SERVER_DATE_FORMAT)
#     }
