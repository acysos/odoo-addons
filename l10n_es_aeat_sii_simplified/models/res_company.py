# -*- coding: utf-8 -*-
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    simplified_journal_id = fields.Many2one(
        string='Simplified Journal', comodel_name='account.journal')
    simplified_limit = fields.Float(string='Simplified Limit', default=400.0)
    