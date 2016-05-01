# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class EventOrder(models.Model):
    _inherit = 'farm.event.order'

    general_feed_event = fields.Many2one(
                            comodel_name='farm.general.feed.event',
                            string='General feed event Order')
