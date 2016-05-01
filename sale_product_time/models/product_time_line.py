# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp
from datetime import datetime
import time

class ProductTimeLine(models.Model):
    _name = 'product.time.line'

    @api.one
    @api.depends('type', 'date')
    def _get_start_datetime(self):
        hour = int(self.type.start_time)
        min = int((self.type.start_time - hour)*60)
        if hour < 10:
            hour = '0'+str(hour)
        else:
            hour = str(hour)
        if min < 10:
            min = '0'+str(min)
        else:
            min = str(min)  
        res = self.date + ' ' + hour + ':' + min + ':00'
        self.start_datetime = res
        
    @api.one
    @api.depends('quantity', 'seconds')
    def _get_total_seconds(self):
        self.total_seconds = self.quantity * self.seconds

    date = fields.Date(string='Date')
    quantity = fields.Float(digits_compute=dp.get_precision('Account'),
                                  string='Quantity')
    seconds = fields.Integer(string='Seconds')
    total_seconds = fields.Integer(string='Total Seconds',
                                   compute='_get_total_seconds')
    type = fields.Many2one('product.time.type', 'Type')
    sale_order_line_id = fields.Many2one('sale.order.line',
                                      string='Sale Order Line')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='sale_order_line_id.order_id.partner_id',
        string='Partner', store=True)
    start_datetime = fields.Datetime(string='Start Date',
                                     compute='_get_start_datetime')
    
class ProductTimeType(models.Model):
    _name = 'product.time.type'
    
    name = fields.Char(string='Name')
    start_time = fields.Float('Time start')
    end_time = fields.Float('Time end')
    