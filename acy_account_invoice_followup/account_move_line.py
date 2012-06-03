# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

import time
import netsvc
from osv import fields, osv
from tools.translate import _

from datetime import datetime, date

import tools

class account_move_line(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'
    _columns = {
        'date_followup': fields.date('Last followup'),
        'invoice_sent': fields.boolean('Sent'),
        'invoice_received': fields.boolean('Received'),
        'invoice_enter': fields.boolean('Entered'),
        'invoice_rejected': fields.boolean('Rejected'),
        'notes': fields.text('Followup Notes'),
    }
    
    def date_change(self, cr, uid, ids):
        res={}
        res['value']={}
        res['value']['date_followup']= time.strftime('%Y-%m-%d')
        return res
        
account_move_line()