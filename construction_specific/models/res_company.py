# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    human_cost = fields.Float(string='Work force cost')
    sign1 = fields.Binary(string="Sing 1")
    sign2 = fields.Binary(string="Sing 2")
