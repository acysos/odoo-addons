# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    edi_path = fields.Char(string='Ruta ficheros EDI')
    out_char_separator = fields.Char(string='Separador archivo de salida')
    edi_node = fields.Char(string='Node Out')
    edi_node_out_refund = fields.Char(string='Node Out Refund')
    edi_sscc_init = fields.Char(string='SSCC Init')
    edi_sscc_code = fields.Char(string='SSCC Code')
