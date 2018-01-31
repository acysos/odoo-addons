# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions


class Rappel(models.Model):
    _inherit = 'rappel'

    product_ids = fields.Many2many(string='Product list',
                                   comodel_name='product.product')

    @api.multi
    def get_products(self):
        product_obj = self.env['product.product']
        product_ids = self.env['product.product']
        for rappel in self:
            if not rappel.global_application and rappel.product_ids:
                ids = rappel.product_ids.mapped('id')
                product_ids += product_obj.search(
                        [('id', 'in', ids)])
                return [x.id for x in product_ids]
            else:
                return super(Rappel, self).get_products()

    @api.constrains('global_application', 'product_id', 'product_categ_id',
                    'product_ids')
    def _check_application(self):
        if not self.global_application and not self.product_id \
                and not self.product_categ_id and not self.product_ids:
            raise exceptions.\
                ValidationError(_('Product and category are empty'))
