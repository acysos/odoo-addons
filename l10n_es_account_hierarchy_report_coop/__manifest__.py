# -*- coding: utf-8 -*-
# Copyright 2017 Joaquin Gutierrez Pedrosa <joaquin@gutierrezweb.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Account Hierarchy Report - Cooperatives",
    'version': "10.0.0.8.0",
    'summary': "Account Hierarchy Report - Cooperatives",
    'sequence': 51,
    'category': "Accounting",
    'author': "Acysos S.L.",
    'license': "AGPL-3",
    'website': "https://www.acysos.com",
    'images': [
    ],
    'depends': [
        "l10n_es_account_hierarchy_report",
        "l10n_es_coop",
    ],
    'data': [
        "data/account.xml",
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
