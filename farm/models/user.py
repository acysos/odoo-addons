# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class User(models.Model):
    _inherit = 'res.users'

    farm = fields.Many2many(comodel_name='res.user_stock.location',
                            inverse_name='user', colum1='location',
                            string='Farms',
                            domain=[('type', '=', 'warehouse'), ],
                            help="Farms to which this user is assigned."
                            "Determine animals that he/she can manage.")


class UserLocation(models.Model):
    _name = 'res.user_stock.location'

    user = fields.Many2one(comodel_name='res.users', string='User',
                           ondelete='CASCADE', required=True, select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location', ondelete='CASCADE',
                               required=True, select=True)
