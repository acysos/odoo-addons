# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    extra_price_qty = fields.Float(string='Quantity per unit',
                                   default=1.0)
