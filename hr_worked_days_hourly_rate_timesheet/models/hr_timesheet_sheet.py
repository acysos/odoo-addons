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


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    worked_rate = fields.Many2one(string='Worked Rate',
                                  comodel_name='hr.payslip.worker.rate')

    @api.model
    def on_change_unit_amount2(self, id, prod_id, unit_amount, company_id,
                              unit=False, journal_id=False, worked_rate_id=False):
        res = super(HrAnalyticTimesheet, self).on_change_unit_amount(
            id, prod_id, unit_amount, company_id, unit=False, journal_id=False)
        if worked_rate_id:
            worked_rate = self.env['hr.payslip.worker.rate'].browse(worked_rate_id)
            if worked_rate:
                value = res['value']
                value['amount'] = value['amount'] * worked_rate.rate
                res['value'] = value
        return res
