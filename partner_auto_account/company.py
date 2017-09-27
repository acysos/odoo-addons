# -*- encoding: utf-8 -*-
########################################################################
#
# Copyright (c) 2011 NaN Projectes de Programari Lliure, S.L. All Rights Reserved.
#                    http://www.NaN-tic.com
# @authors: Ignacio Ibeas <ignacio@acysos.com
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

from openerp.tools.translate import _
from openerp.osv import orm, fields

class res_company(orm.Model):
    _inherit = 'res.company'
    
    _columns = {
        'parent_receivable_account_id': fields.many2one('account.account', 'Receivable Account', domain="[('type','=','view'),('company_id','=',active_id)]", help='If set, a receivable account will be created for all partners with the "Customer" flag set.'),
        'parent_payable_account_id': fields.many2one('account.account', 'Payable Account', domain="[('type','=','view'),('company_id','=',active_id)]", help='If set, a payable account will be created for all partners with the "Supplier" flag set.'),
        'account_digits': fields.integer('Number of digits', help='Indicates the number of digits to be used for automatically created receivable and payable partner accounts.'),
    }