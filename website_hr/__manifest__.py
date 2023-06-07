# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2020  Acysos S.L.
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
    "name": "Website HR attendance",
    "version": "14.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Alexander Ezquevo <alexander@acysos.com>', ],
    "category": "",
    "license": "AGPL-3",
    "description": """HR attendance in website""",
    "depends": ['website', 'hr_attendance_portal_inout', 'portal'],
    "data": ['views/website.xml', 'views/hr_enployee_views.xml'],
    "installable": True,
}
