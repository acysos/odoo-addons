# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Suministro Inmediato de Información - Factura simplificada (POS)",
    "version": "11.0.0.1.1",
    "category": "Accounting & Finance",
    "website": "https://www.acysos.com",
    "author": "Acysos S.L.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": ["zeep",
                   "requests"],
    },
    "depends": [
        "l10n_es",
        "l10n_es_aeat_sii",
        "l10n_es_pos"
    ],
    "data": [
        'views/point_of_sale_view.xml'
    ],
}
