# -*- coding: utf-8 -*-
# Copyright 2019 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class AeatModelExportConfigLine(models.Model):
    _inherit = 'aeat.model.export.config.line'
    
    line_crlf = fields.Boolean(string='Line CRLF')
    