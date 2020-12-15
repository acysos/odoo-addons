# Copyright 2020 Ignacio Ibeas <ignacio@acysos.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _


class ProductEan13(models.Model):
    _inherit = 'product.ean13'
    
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
