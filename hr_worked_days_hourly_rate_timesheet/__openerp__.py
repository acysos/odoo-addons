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

{
    'name': 'Worked Days Hourly Rates',
    'version': '1.0',
    'author': 'Acysos SL',
    'license': 'AGPL-3',
    'category': 'Sale Management',
    'depends': ['hr_worked_days_hourly_rate',
                'hr_worked_days_from_timesheet',
                'hr_payroll'],
    'demo': [],
    'data': ['views/hr_timesheet_sheet_view.xml',
             'views/hr_payslip_view.xml',
             'views/hr_payslip_worker_rate.xml'],
    'auto_install': False,
    'installable': True,
}
