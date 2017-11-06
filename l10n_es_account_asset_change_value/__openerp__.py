# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Spanish Localization - Account Asset Change Value",
    "version": "8.0.0.0.1",
    "category": "Accounting & Finance",
    "website": "https://www.acysos.com",
    "author": "Acysos S.L.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_asset",
        "l10n_es_account_asset"
    ],
    "data": [
        "views/account_invoice_view.xml",
        "wizards/account_asset_change_value_view.xml",
        "views/account_asset_view.xml"
    ]
}
