# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _get_density(self):
        for product in self:
            if product.volume != 0:
                product.density = product.weight_net / product.volume

    density = fields.Float(
        string='Thickness',
        compute=_get_density,
        help='Density is in kg/m3. Calculated from net weight and volume.')
    thickness = fields.Float(string='thickness', help='Thickness is in mm.')
    wide = fields.Float('Wide', help='Wide is in mm.')
    diameter = fields.Float('Diameter', help='Diameter is in mm.')
    length = fields.Float('Length', help='Lenght is in mm.')
