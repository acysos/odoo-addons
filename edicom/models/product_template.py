# -*- coding: utf-8 -*-
# Copyright 2020 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    edicom_tipart = fields.Selection(
        string='Tipo articulo',
        related='product_variant_ids.edicom_tipart',
        selection=[('CU', 'Unidad de consumo'), ('DU', 'Unidad de expedición'),
                   ('TU', 'Unidad Comerciada'),
                   ('VQ', 'Producto de medida variable')],
        default='CU')
