# -*- coding: utf-8 -*-
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Balance Reporting exclude Journals",
    "version": "10.0.0.1.0",
    "category": "Accounting & Finance",
    "website": "https://www.acysos.com",
    "author": "Acysos S.L.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_balance_reporting",
    ],
    "data": [
        "views/account_balance_reporting_report_view.xml",
    ],
}
