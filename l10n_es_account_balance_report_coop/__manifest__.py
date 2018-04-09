# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Informes de cuentas anuales españoles - Cooperativas",
    "version": "8.0.0.1.0",
    "author": "Acysos S.L.",
    "contributors": [
        "Ignacio Ibeas <ignacio@acysos.com>"
    ],
    "license": "AGPL-3",
    "website": "http://www.acysos.com",
    "category": "Localisation/Accounting",
    "depends": [
        'l10n_es',
        'account_balance_reporting',
    ],
    "demo": [],
    "data": [
        'data/balance_abreviado_coop.xml',
        'data/balance_pymes_coop.xml',
        'data/balance_normal_coop.xml',
        'data/pyg_abreviado_coop.xml',
        'data/pyg_pymes_coop.xml',
        'data/pyg_normal_coop.xml',
    ],
    "installable": True,
}
