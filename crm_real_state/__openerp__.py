# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2015  Acysos S.L.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################
{
    "name": "CRM for real state",
    "version": "1.0",
    "depends": ["base", "acy_real_state", "poweremail", "crm"],
    "author": "Acysos S.L.",
    "website": "http://www.acysos.com",
    "category": "Specific Industry",
    "complexity": "normal",
    "description": """
    """,
    "init_xml": [],
    'update_xml': ['crm_lead_view.xml',
                   'company_view.xml',
                   'crm_lead_data.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
