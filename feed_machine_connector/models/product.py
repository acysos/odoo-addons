# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    feed_machine_product_id = fields.Char(string='External Id')


class Product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        displayName = []
        for product in self:
            if product.product_tmpl_id.feed_machine_product_id:
                displayName.append(
                    (product.id, product.name_template + '-' +
                    product.product_tmpl_id.feed_machine_product_id))
            else:
                displayName.append((product.id, product.name_template))
        return displayName
