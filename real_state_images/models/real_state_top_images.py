# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3).

from openerp import api, fields, models


class RealStateTop(models.Model):
    _name = 'real.state.top'
    _inherit = [_name, "base_multi_image.owner"]

    # Make this field computed for getting only the available images
    image_ids = fields.One2many(comodel_name="base_multi_image.image")
    image_main = fields.Binary(inverse="_inverse_main_image_large")
    image_main_medium = fields.Binary(inverse="_inverse_main_image_medium")
    image_main_small = fields.Binary(inverse="_inverse_main_image_small")

    @api.multi
    def _inverse_main_image(self, image):
        for top in self:
            if image:
                top.image_ids[0].write({
                    'file_db_store': image,
                    'storage': 'db',
                })
            else:
                top.image_ids = [(3, top.image_ids[0].id)]
                
    @api.multi
    def _inverse_main_image_large(self):
        for top in self:
            top._inverse_main_image(top.image_main)

    @api.multi
    def _inverse_main_image_medium(self):
        for top in self:
            top._inverse_main_image(top.image_main_medium)

    @api.multi
    def _inverse_main_image_small(self):
        for top in self:
            top._inverse_main_image(top.image_main_small)


