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
from openerp import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def _timesheet_mapping(self, timesheet_sheets, payslip, date_from,
                           date_to):

        super(HrPayslip, self)._timesheet_mapping(
            timesheet_sheets, payslip, date_from, date_to)

        wr_ids = self.env['hr.payslip.worker.rate'].search([])
        if wr_ids:
            for line in self.worked_days_line_ids:
                hours = {}
                for ts in line.timesheet_sheet_id.timesheet_ids:
                    if date_from <= ts.date <= date_to:
                        if ts.worked_rate.id not in hours:
                            hours[ts.worked_rate.id] = ts.unit_amount
                        else:
                            hours[ts.worked_rate.id] += ts.unit_amount
                for wr in wr_ids:
                    if wr.id in hours:
                        hourly_rate = 0
                        if payslip.employee_id.product_id:
                            prod = payslip.employee_id.product_id
                            hourly_rate = prod.standard_price
                        line2 = line.copy()
                        line2.rate = wr.rate
                        line2.hourly_rate = hourly_rate
                        line2.number_of_hours = hours[wr.id]
                        line2.worked_rate = wr.id
                line.unlink()
