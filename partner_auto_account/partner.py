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

class res_partner(orm.Model):
    _inherit = 'res.partner'

    def update_account(self, cr, uid, partner_id, account_type, context, force_checked=None):
            
        if account_type not in ('receivable', 'payable'):
            return

        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        parent_account = getattr(company, 'parent_%s_account_id' % account_type )
        if not parent_account:
            return

        partner = self.browse(cr, uid, partner_id, context)
        if account_type == 'receivable':
            checked = partner.customer
        else:
            checked = partner.supplier
        partner_account = getattr(partner, 'property_account_%s' % account_type )

        if not force_checked is None:
            checked = force_checked

        if partner_account:
            if checked:
                # If account already exists, just check if we need to update account name.
                if partner_account.name != partner.name:
                    # We will only update account name if no other partner is using the same account.
                    value = 'account.account,%d' % partner_account.id
                    partners = self.pool.get('ir.property').search(
                        cr, uid, [('res_id','!=',False),
                                  ('value_reference','=',value)],
                        context=context)
                    if len(partners) == 1:
                        self.pool.get('account.account').write(
                            cr, uid, [partner_account.id], {
                                'name': partner.name,
                            }, context)
                        return
            
            # If it's not possible to unlink the account we will rollback this change
            # so the property remains the same. Note that we cannot try to unlink first, 
            # because in this case it would always fail because of the fact that it's set
            # as the account in the partner.
            cr.execute('SAVEPOINT remove_account')
            self.write(cr, uid, [partner_id], {
                'property_account_%s' % account_type : False,
            }, context)
            try:
                # Unlink may raise an exception if the account is already set in another partner
                # or if it has account moves.
                if partner_account.name == partner.name:
                    self.pool.get('account.account').unlink(cr, uid, [partner_account.id], context)
            except orm.except_orm:
                cr.execute('ROLLBACK TO SAVEPOINT remove_account')

            cr.execute('RELEASE SAVEPOINT remove_account')

        if not checked:
            return
        
        sequence_obj = self.pool.get('ir.sequence')
        sequence_id = sequence_obj.search(cr, uid, [('code','=','res.partner')], 
                                       context=context)
        sequence = sequence_obj.browse(cr, uid, sequence_id, 
                                       context=context)[0]
                                       
                   
        partner_ref = partner.ref or ''
        digits = company.account_digits or 0
        code = parent_account.code + '0'*(digits - len(parent_account.code + partner_ref)) + partner_ref

        account_id = self.pool.get('account.account').search(cr, uid, [('code','=',code)], context=context)
        if account_id:
            account_id = account_id[0]
        else:
            account_id = self.pool.get('account.account').create(cr, uid, {
                'name': partner.name,
                'code': code,
                'parent_id': parent_account.id,
                'user_type': parent_account.user_type.id,
                'reconcile': True,
                'type': account_type,
            }, context)
        self.write(cr, uid, [partner_id], {
            'property_account_%s' % account_type : account_id,
        }, context)


    def create(self, cr, uid, vals, context=None):
        id = super(res_partner, self).create(cr, uid, vals, context)
        self.update_account(cr, uid, id, 'receivable', context)
        self.update_account(cr, uid, id, 'payable', context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        result = super(res_partner, self).write(cr, uid, ids, vals, context)
        if 'customer' in vals or 'name' in vals:
            for id in ids:
                self.update_account(cr, uid, id, 'receivable', context)
        if 'supplier' in vals or 'name' in vals:
            for id in ids:
                self.update_account(cr, uid, id, 'payable', context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        for id in ids:
            self.update_account(cr, uid, id, 'receivable', context, force_checked = False)
            self.update_account(cr, uid, id, 'payable', context, force_checked = False)
        return super(res_partner, self).unlink(cr, uid, ids, context)
