# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Suministro Inmediato de Información - REAGYP",
    "version": "10.0.1.0.0",
    "author": "Acysos S.L.",
    "website": 'https://www.acysos.com',
    "category": "Localization/Account Charts",
    "license": "AGPL-3",
    "depends": [
        "l10n_es",
        "l10n_es_reagp",
        "l10n_es_aeat_sii"
    ],
    "data": [
        "data/account_fiscal_position_data.xml",
        "data/aeat_sii_map_data.xml"
    ],
    'installable': True,
}
