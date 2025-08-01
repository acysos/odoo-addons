# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2024  Acysos S.L.
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
    "name": "Farm",
    "version": "17.0.0.0",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Alexander Ezquevo <alexander@acysos.com>', ],
    "category": "Specific industry",
    "license": "AGPL-3",
    "description": """Farm Management System""",
    "depends": ["account","stock", "sale", "purchase", "sale_stock",],
    "data": ["security/farm_security.xml", 'security/ir.model.access.csv',"views/specie.xml", "views/event_order.xml", "views/consume_stock.xml", "views/abstract_event.xml",
             "views/feed_event.xml", "views/medication_event.xml","views/animal.xml", "views/animal_group.xml", "views/farrowing_event.xml",
             "views/semen_extraction_event.xml", "views/removal_event.xml", "views/stock.xml", "views/menu.xml",
                "views/product.xml",
    ],
    "installable": True,
}
