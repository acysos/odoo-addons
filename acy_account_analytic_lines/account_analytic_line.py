# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

class account_analytic_view_line(osv.osv_memory):
    _name = "account.analytic.view.line"
    _description = "Account Analytic View Line"
    _inherit = "ir.wizard.screen"
    
    
    _columns = {
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account',required=True),
        'children': fields.boolean('With children'),
    }
    
    def open_account_analytic_lines(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        analytic_obj = self.pool.get('account.analytic.account').browse(cr,uid,[data['analytic_id']])[0]
        accounts = []
        accounts.append(analytic_obj.id)
        if data['children'] == 1:
            for child in analytic_obj.child_complete_ids:
                accounts.append(child.id)
        res = {
            'domain': str([('account_id','in',accounts)]),
            'name': 'Analytic account lines',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res
    
account_analytic_view_line()