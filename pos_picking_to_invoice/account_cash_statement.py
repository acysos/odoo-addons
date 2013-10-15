# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

from osv import osv
from osv import fields
import decimal_precision as dp
from tools.translate import _
import time

class account_cash_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def button_confirm_cash(self, cr, uid, ids, context=None):
        statement_obj = self.pool.get('account.bank.statement')
        print "Button"
        print ids
        for statement in statement_obj.browse(cr, uid, ids, context=context):
            if statement.journal_id.to_invoiced:
                return self.write(cr, uid, ids, {'closing_date': time.strftime("%Y-%m-%d %H:%M:%S"),'state':'confirm'}, context=context)
            else:
                res = super(account_cash_statement, self).button_confirm_cash(cr, uid, ids, context=context)
                return res
    
account_cash_statement()