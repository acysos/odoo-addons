# -*- coding: utf-8 -*-
# Copyright 2020 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    edicom_tipart = fields.Selection(
        string='Tipo articulo',
        selection=[('CU', 'Unidad de consumo'), ('DU', 'Unidad de expedición'),
                   ('TU', 'Unidad Comerciada'),
                   ('VQ', 'Producto de medida variable')],
        default='CU')
