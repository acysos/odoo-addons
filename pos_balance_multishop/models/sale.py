# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _
import openerp.addons.decimal_precision as dp


class balance_sale_shop(models.Model):
    _name = 'balance.sale.shop'

    name = fields.Char('name')
    balance_ids = fields.One2many(
        comodel_name='sale.balance', inverse_name='shop_id',
        string='Balances')
