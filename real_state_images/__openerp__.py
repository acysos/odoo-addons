# -*- coding: utf-8 -*-
# © 2013 Ignacio Ibeas <ignacio@acysos.com>
# © 2017 Daniel Pascal <daniel@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multiple Images in Products",
    "version": "8.0.2.0.0",
    "author": "Acysos S.L.,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "http://www.serviciosbaeza.com",
    "category": "Sales Management",
    "depends": [
        "base_multi_image",
        "real_state"
    ],
    "init_xml": [],
    "demo_xml": [],
    "data": [
        'views/real_state_top_images_view.xml',
    ],
    'installable': True,
}
