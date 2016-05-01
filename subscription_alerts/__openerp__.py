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
    "name": "Subscription Alerts",
    "version": "8.0.1.0",
    "author": "Acysos S.L.",
    'website': 'https://www.acysos.com/',
    "category": "Generic Modules/Tools",
    "summary": "Send mail alerts before a subcription copy.",
    "license": "AGPL-3",
    "depends": ["base",
                "subscription",
                "email_template",
                ],
    "data": ['views/res_company_view.xml',
             'views/subscription_view.xml',
             'data/subscription_alerts_cron.xml'],
    "active": False,
    "installable": True,
}
