# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import tools
import os
from datetime import datetime

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def _get_invoice_date(self, cr, uid, ids, field_name, arg, context=None):
         lines = self.pool.get('account.invoice.line').browse(cr, uid, ids, context)
         res={}
         for line in lines:
             res[line.id] = line.invoice_id.date_invoice
         return res
         
    def _invoice_date_search(self, cr, uid, obj, name, args, context=None):
        if not len(args):
            return []
        operator = args[0][1]
        value = args[0][2]
        if not value:
            return []
        now = datetime.now()
        date = value.split('-')
        if value == 'False':
            cr.execute("SELECT l.id " \
                    "FROM account_invoice_line l, account_invoice i " \
                    "WHERE l.invoice_id = i.id AND i.date_invoice is NULL")
        else:
            if datetime(int(date[0]),int(date[1]),int(date[2])) > now:
                cr.execute("SELECT l.id " \
                    "FROM account_invoice_line l, account_invoice i " \
                    "WHERE l.invoice_id = i.id AND i.date_invoice is NULL")
            else:
                cr.execute(("SELECT l.id " \
                    "FROM account_invoice_line l, account_invoice i " \
                    "WHERE l.invoice_id = i.id AND i.date_invoice %s '%s'") % (operator,value))
        res = cr.fetchall()
        if len(res):
            return [('id', 'in', [x[0] for x in res])]
        else:
            return [('id','=','0')]

    _columns = {
        'invoice_date': fields.function(_get_invoice_date,method=True, type='date', string='Invoice Date', select=1, fnct_search=_invoice_date_search)
    }
    
account_invoice_line()