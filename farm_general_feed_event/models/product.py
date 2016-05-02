# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class Template(models.Model):
    _inherit = 'product.template'

    feed_general = fields.Boolean(string='General Feed',
                                    default=False)
    feed_lactating = fields.Boolean(string='Feed For Lactaing Animals',
                                    default=False)
    feed_transit = fields.Boolean(string='Feed for Transition Animals',
                                  default=False)
