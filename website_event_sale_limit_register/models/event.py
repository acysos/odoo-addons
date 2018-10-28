# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _    
    
class EventEvent(models.Model):
    _inherit = 'event.event'
    
    limit_per_registration = fields.Integer(
        string='Limit per registration',
        help="""Limit the number of registration in each order.
        If the value is 0 is not limit.""")
