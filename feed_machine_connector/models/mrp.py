# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class mrpProductiom(models.Model):
    _inherit = 'mrp.production'

    machine_production_lot = fields.Char(string='Machine Production lot')


class mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    bom_report = fields.Html(string='Ensabched BOM')
