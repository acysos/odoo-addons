# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
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
    "name": "Addon for Animal farms",
    "version": "8.1",
    "license": "AGPL-3",
    "author": "Acysos S.L.",
    "website": "www.acysos.com",
    "contributors": ['Alexander Ezquevo alexander@acysos.com', ],
    "images": [],
    "category": "Specific IndustrY",
    "depends": [
        "product",
        "stock",
        "mrp",
        "mrp_lot_cost",
        "purchase",
        "account",
    ],
    "data": [
        "views/specie.xml",
        "views/tag.xml",
        "views/event_order.xml",
        "views/abstract_event.xml",
        "views/feed_event.xml",
        "views/medication_event.xml",
        "views/product.xml",
        "views/animal.xml",
        "views/breed.xml",
        "views/animal_group.xml",
        "views/stock.xml",
        "views/abort_event.xml",
        "views/pregnancy_diagnosis_event.xml",
        "views/farrowing_event.xml",
        "views/foster_event.xml",
        "views/insemination_event.xml",
        "views/move_event.xml",
        "views/removal_event.xml",
        "views/weaning_event.xml",
        "views/trasformation_event.xml",
        "views/production.xml",
        "views/semen_extraction_event.xml",
        "views/consume_stock.xml",
        "views/farm_menu.xml",
        "views/res_company.xml",
        "views/event_move.xml",
        "data/farm_data.xml",
        "views/purchase_analytics.xml",
        "views/account_invoice.xml",
        "security/farm_security.xml",
        "security/ir.model.access.csv",
        
    ],
    "installable": True,
}
