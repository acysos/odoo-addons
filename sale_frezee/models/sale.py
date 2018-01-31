# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    refrigeration_type = fields.Selection(string='Order tipe',
                                  selection=[('no', 'No regrigerated'),
                                             ('refri','refrigerated'),
                                             ('fre', 'Frezee')],
                                          default='refri')
    