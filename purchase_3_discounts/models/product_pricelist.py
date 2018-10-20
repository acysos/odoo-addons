# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class product_pricelist(models.Model):
    _inherit = 'product.pricelist'

    visible_discount = fields.Boolean(string='Visible Discount', default=True)
