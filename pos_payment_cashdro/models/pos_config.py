# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    cashdro_payment_terminal = fields.Boolean(string='Cashdro Payment Terminal')
    cashdro_ip = fields.Char(string='Cashdro IP Address',  size=45)
    cashdro_user = fields.Char(string='Cashdro User')
    cashdro_password = fields.Char(string='Cashdro Password')
    
