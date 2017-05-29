# -*- coding: utf-8 -*-
# © 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multiple Images in Products",
    "version": "8.0.2.0.0",
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería, "
              "Tecnativa, "
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
