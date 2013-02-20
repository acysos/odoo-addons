# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2010 NaN Projectes de Programari Lliure, S.L. All Rights Reserved.
#                    http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _

class account_move(osv.osv):
    _inherit = 'account.move'

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if context is None:
            context = {}

        if name and name.lstrip().startswith('*'):
            id = name.strip().lstrip('*').strip()
            try:
                id = int(id)
            except ValueError:
                id = False

            if id and self.search(cr, user, [('id','=',id)], context=context):
                    return self.name_get(cr, user, [id], context)

        return super(account_move, self).name_search(cr, user, name, args, operator, context, limit)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        move_line_values = {}
        if 'journal_id' in vals:
            move_line_values['journal_id'] = vals['journal_id'],
        if 'period_id' in vals:
            move_line_values['period_id'] = vals['period_id'],

        if move_line_values:
            ctx = context.copy()
            ctx['propagate_journal_period'] = False
            line_ids = []
            for move in self.browse(cr, uid, ids, context):
                line_ids += [x.id for x in move.line_id]
            self.pool.get('account.move.line').write(cr, uid, line_ids, move_line_values, ctx)
            
        return super(account_move, self).write(cr, uid, ids, vals, context)

account_move()

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if context is None:
            context = {}
        if context.get('propagate_journal_period',True):
            move_values = {}
            if 'journal_id' in vals:
                move_values['journal_id'] = vals['journal_id']
            if 'period_id' in vals:
                move_values['period_id'] = vals['period_id']

            if move_values:
                move_ids = []
                for move_line in self.browse(cr, uid, ids, context):
                    if ('journal_id' in move_values and move_line.journal_id.id != move_values['journal_id']) or ('period_id' in move_values and move_line.period_id.id != move_values['period_id']):
                        move_ids.append( move_line.move_id.id )
                self.pool.get('account.move').write(cr, uid, move_ids, move_values, context)
        return super(account_move_line, self).write(cr, uid, ids, vals, context, check, update_check)

account_move_line()
    

class account_account(osv.osv):
    _inherit = 'account.account'

    def copy(self, cr, uid, id, default={}, context={}, done_list=[], local=False):
        account = self.browse(cr, uid, id, context=context)
        new_child_ids = []
        if not default:
            default = {}
        default = default.copy()
        default['code'] = (account['code'] or '') + _('(copy)')
        if not local:
            done_list = []
        if account.id in done_list:
            return False
        done_list.append(account.id)
        default['child_parent_ids'] = [(6, 0, [])]
        return super(account_account, self).copy(cr, uid, id, default, context=context)
account_account()

class account_journal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'group_products': fields.boolean('Group Products', help='If set, it will group all invoice lines even if they have different products. Note that if products have the different accounts they will not be grouped.'),
        'group_products_text': fields.char('Account Move Line Text', size=64, help='If "Group Products" is set and this field is not empty, this text will be used as description for all account move lines.'),
        'check_invoice_number_date': fields.boolean('Check invoice date and number', help='If set, ensures no invoice number is created with a date previous to an existing invoice.'),
    }

account_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

