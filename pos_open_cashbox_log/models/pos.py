# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from datetime import date, time, datetime

class PosOpenCashboxLog(models.Model):
    _name = 'pos.open.cashbox.log'

    name = fields.Char(string='Reason', default='Open Cashbox')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    session_id  = fields.Many2one('pos.session','Session')
    open_date = fields.Datetime(string='Date', default=fields.Datetime.now)
    
    def open_cashbox(self, reason, cashier, session_id):
        vals = {
            'name': reason,
            'user_id': cashier,
            'session_id': session_id
        }
        self.create(vals)
        return True
