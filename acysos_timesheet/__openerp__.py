# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 NaN Projectes de Programari Lliure, S.L.. All Rights Reserved
#                       http://www.NaN-tic.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
	"name" : "Acysos Task Manager",
	"version" : "1.0",
	"description" : """Modifies the original project_timesheet module for Acysos project.
    - Description:
      Simplified task management.
      Initial screen where it asks for the employee and the Draft Code. The next screen shows the list of tasks available for the selected project. This screen gives the option to start the selected task or end it. If you start a task without task open previously closed, the system automatically closes the previous task with the current end date.
    - Requirements:
      + Employees must be assigned to OpenERP users
      + Employees must have assigned a product and a journal on timesheet tab
      + Projects must be defined using an analytical account
    
    Sponsored by Talleres Mutilva""",
	"author" : "Acysos S.L., NaN Projectes de Programari LLiure S.L.",
	"website" : "http://www.acysos.com",
	"license" : "AGPL-3",
	"depends" : [ 
        'project',
        'project_timesheet',
        'hr_attendance',
        'acy_project_with_tasks'
        ], 
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [ 
        'timesheet_wizard.xml',
        'security/ir.model.access.csv'
        ],
	"active": False,
	"installable": True
}
