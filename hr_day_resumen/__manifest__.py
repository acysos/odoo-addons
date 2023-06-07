# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2022  Acysos S.L.
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
    "name": "hr day resumen",
    "version": "14.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Alexander Ezquevo <alexander@acysos.com>', ],
    "category": "",
    "license": "AGPL-3",
    "description": """ Resumen diario de asistencia vs horas teoricas
    """,
    "depends": ["hr_holidays_holidays", "hr_attendance", "hr_holidays_public"],
    "data": ["views/resumen_views.xml", "wizards/fix_hours_views.xml", 
             "views/hr_resume_report_views.xml",
             "security/ir.model.access.csv","wizards/change_calendar_view.xml",
             "views/hr_employee_view.xml", "views/hr_leave.xml", "views/overtime.xml",
             "wizards/overtime_modify_view.xml"
             ],
    "installable": True,
}
