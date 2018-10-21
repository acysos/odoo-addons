# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    note = fields.Text(
        string='Note',
        translate=True)
