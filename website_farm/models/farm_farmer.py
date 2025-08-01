# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class FarmFarmer(models.Model):
    _name = 'farm.farmer'

    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    specie_ids = fields.Many2one(string="specie", comodel_name="farm.specie")
    farm_ids = fields.Many2many(string="farm", comodel_name="stock.location")