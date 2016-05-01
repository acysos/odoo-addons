# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2016 Acysos S.L. (http://acysos.com)
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
    "name": "Machinery Manager Project",
    "version": "8.0.1.0",
    "author": "Acysos S.L.",
    'website': 'https://www.acysos.com/',
    "category": "Generic Modules/Project Management",
    "summary": "Add machinery to project and task",
    "license": "AGPL-3",
    "depends": ["project",
                "machine_manager",
                ],
    "data": ['views/project_view.xml',
             'views/machinery_view.xml'],
    "active": False,
    "installable": True,
}
