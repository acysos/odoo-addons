# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class Res_company(models.Model):
    _inherit = 'res.company'

    feed_account = fields.Many2one(comodel_name='account.account',
                                   string='Consumed Feed Account')
