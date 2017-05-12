# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2017  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    raw_material = fields.Boolean(string='Raw material', default=False)
