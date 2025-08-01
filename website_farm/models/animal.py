# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

class FarmAnimal(models.Model):
    _inherit = 'farm.animal'

    farm_origin = fields.Char(string='Origin')

class FarmAnimalGroup(models.Model):
    _inherit = 'farm.animal.group'

    farm_origin = fields.Char(string='Origin')