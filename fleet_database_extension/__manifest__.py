# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vehicle Database",
    "version": "1",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Ignacio Ibeas <ignacio@acysos.com>'],
    "category": "",
    "license": "AGPL-3",
    "depends": [
        'fleet',
    ],
    "data": [
        'views/fleet_vehicle_view.xml',
        'security/ir.model.access.csv'
    ],
    'images': ['static/description/banner.jpg'],
    "installable": True,
}
