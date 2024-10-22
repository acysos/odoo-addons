# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
#           Daniel Pascal <daniel@acysos.com>
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
    "name": "CRM for real estate",
    "version": "14.0.1.0.0",
    "author": "Acysos S.L.",
    "website": "http://www.acysos.com",
    "license" : "AGPL-3",
    "complexity": "normal",
    "category": "Specific Industry",
    "depends": ['base',
                'real_estate_base',
                'crm'],
    "init_xml": [],
    "demo_xml": [],
    "data": ['security/ir.model.access.csv',
             'views/crm_lead_view.xml',
             #'views/crm_action_view.xml',
             #'views/res_partner_view.xml',
             'views/company_view.xml',
             #'data/crm_lead_data.xml'
             ],
    "active": False,
    "installable": True
}
