# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _
import openerp.addons.decimal_precision as dp


class balance_model(models.Model):
    _name = 'balance.model'
    _description = 'balance.model'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)


class sale_balance(models.Model):
    _name = 'sale.balance'

    name = fields.Char('Name', required=False, readonly=False)
    shop_id = fields.Many2one(comodel_name='balance.sale.shop', string='Shop')
    network = fields.Boolean('Network Connection', required=False)
    model_id = fields.Many2one(
        comodel_name='balance.model', string='Balance Model', required=False)
    ip = fields.Char('IP', required=False, readonly=False)
    port = fields.Integer('Port')
