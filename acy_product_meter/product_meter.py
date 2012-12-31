# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

class product_meter(osv.osv):
    _name = "product.meter"
    _description = "Product Meter"
    
    _columns = {
        'date': fields.date('Date', select=1),
        'partner_id': fields.many2one('res.partner', 'Partner', select=True, required=True),
        'product_id': fields.many2one('product.product', 'Product', select=True, required=True),
        'meter': fields.float('Meter', digits_compute=dp.get_precision('Decimal Meter')),
        'state': fields.selection([('read', 'Read'),('invoiced', 'Invoiced')], 'State', required=True),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'read',
    }
    
    _order = 'date desc'
    
    _sql_constraints = [
        ('meter_uniq', 'unique(date, partner_id, product_id)', 'Only one meter per day, per partner and per product !'),
    ]
    
product_meter()