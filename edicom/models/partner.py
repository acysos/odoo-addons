# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    codigo_edi = fields.Char(
        string='Codigo Edi', size=17,
        help="Codigo EDI de la empresa.  Es el código EAN13 que asigna AECOC."
             " (p.e. 8411111000000)")
    edicom_matricula = fields.Char(
        string='Matricula Transportista', size=35)
    edicom_decimal = fields.Integer(string='Edicom Decimal', default=2)
