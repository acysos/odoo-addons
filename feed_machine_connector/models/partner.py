# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class partner(models.Model):
    _inherit = 'res.partner'

    feed_machine_ref = fields.Char(string='Feed Machine ref')