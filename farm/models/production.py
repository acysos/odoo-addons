# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class BOM(models.Model):
    _inherit = 'mrp.bom'

    semen_dose = fields.Boolean(string='Semen Dose')
    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Dose Specie')
