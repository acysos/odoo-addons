# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2015  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

from openerp import models, fields

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'
    
    user_ids = fields.Many2many('res.users', string="User perm")
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        print vals
        res = super(account_analytic_account, self).create(cr, uid, vals, context)
        cr.commit()
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'user_ids' in vals:
            vals2 = {}
            vals2['user_ids'] = vals['user_ids']
            for account in self.browse(cr, uid, ids, context):
                for child in account.child_ids:
                    self.write(cr, uid, [child.id], vals2, context)
        super(account_analytic_account, self).write(cr, uid, ids, vals,
                                                    context=None)
        return True

