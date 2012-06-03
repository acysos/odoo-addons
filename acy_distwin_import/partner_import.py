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
import tools
import os
import base64
import time
import re
from datetime import datetime, date
from tools.translate import _

class distwin_partner_import(osv.osv):
    _name = "distwin.partner.import"
    _description = "Distwin Partner Import"
    
    _columns = {
        'name': fields.char('Import Code', size=64, select=1),
        'date': fields.date('Date', required=True, states={'confirm': [('readonly', True)]}),
        'partner_lines': fields.one2many('distwin.partner.line', 'import_id', 'Partner lines', states={'draft':[('readonly',False)]}, readonly=True),
        'state': fields.selection([('draft', 'Draft'),('confirm', 'Confirmed')], 'State', required=True, states={'confirm': [('readonly', True)]}, readonly="1"),
    }
    
    _defaults = {
        'name': '/',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }
    
    _order = 'date'
    
    def action_confirm(self, cr, uid, ids, context=None):
        partners = self.browse(cr,uid,ids,context)[0]
        partner_obj = self.pool.get('res.partner')
        account_obj = self.pool.get('account.account')
        address_obj = self.pool.get('res.partner.address')
        account_type_obj = self.pool.get('account.account.type')
        user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
        for partner_line in partners.partner_lines:
            country_id = self.pool.get('res.country').search(cr,uid,[('name','=',partner_line.address_country)],context=context)
            if not country_id:
                country_id = user.company_id.partner_id.address[0].country_id.id
            state_id = self.pool.get('res.country.state').search(cr,uid,[('name','=',partner_line.address_state),('country_id','=',country_id)],context=context)
            if not state_id:
                state_id = user.company_id.partner_id.address[0].state_id.id
            address_values = {
                'street':partner_line.address_street,
                'city':partner_line.address_city,
                'phone':partner_line.address_phone,
                'zip':partner_line.address_zip,
                'state_id':state_id,
                'country_id':country_id,
            }
            reference = partner_line.account_number[3:]
            partner_id = partner_obj.search(cr,uid,[('ref','=',reference)], context=context)
            if partner_id:
                partner = partner_obj.browse(cr,uid,partner_id,context=context)[0]
                partner_obj.write(cr,uid,partner_id,{'name':partner_line.name,'vat':partner_line.vat_number},context=context)
                address_obj.write(cr,uid,partner.address[0].id,address_values,context=context)
                account_obj.write(cr,uid,partner.property_account_receivable.id,{'name':partner_line.name},context=context)
            else:
                res_ids = account_type_obj.search(cr, uid, [('code', '=', 'terceros - rec')]) # Busca tipo cuenta de usuario rec
                acc_user_type = res_ids and res_ids[0]
                account_values = {
                    'name': partner_line.name,
                    'code': partner_line.account_number,
                    'type': 'receivable',
                    'user_type': acc_user_type,
                    'reconcile': True,
                    'parent_id': user.company_id.parent_receivable_account_id.id
                }
                account_id = account_obj.create(cr,uid,account_values,context=context)
                partner_values = {
                    'ref': reference,
                    'name': partner_line.name,
                    'vat': partner_line.vat_number,
                    'property_account_receivable': account_id,
                    'customer': True,
                    'vat_subjected': True,
                    'include_in_mod347': True,
                    'company_id': user.company_id.id,
                    'lang': user.company_id.partner_id.lang,
                    'active': True,
                    'supplier': False,
                    'employee': False,
                }
                partner_id = partner_obj.create(cr,uid,partner_values,context=context)
                address_values['partner_id'] = partner_id
                address_obj.create(cr,uid,address_values,context=context)
        self.write(cr, uid, ids, {'state': 'confirm'})
        return True
        
    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
distwin_partner_import()

class distwin_partner_line(osv.osv):
    
    _name = "distwin.partner.line"
    _description = "Distwin Partner Line"
    
    _columns = {
        'account_number': fields.char('Number', size=128, select=True),
        'name': fields.char('Name', size=128, required=True, select=True),
        'address_street': fields.char('Street', size=128),
        'address_city': fields.char('City', size=128),
        'address_state': fields.char('State', size=128),
        'address_phone': fields.char('Phone', size=128),
        'address_zip': fields.char('Zip', change_default=True, size=24),
        'address_country': fields.char('Country', change_default=True, size=2),
        'vat_number': fields.char('Vat Number', size=24),
        'import_id': fields.many2one('distwin.partner.import', 'Operator registry', ondelete='cascade'),
    }
distwin_partner_line()

class import_distwin_partner_file_wizard(osv.osv):
    
    _name = 'import.distwin.partner.file.wizard'

    _columns = {
        'file': fields.binary('CSV Partner File', required=True, filename='file_name'),
        'file_name': fields.char('CSV Partner File', size=64, readonly=True),
        }
        
    def import_action(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        import_partner_obj = self.pool.get('distwin.partner.import')
        partner_line_obj = self.pool.get('distwin.partner.line')
        
        for distwin_wizard in self.browse(cr,uid,ids,context):
            import_partner_id = context['active_id']
            import_partner = import_partner_obj.browse(cr, uid, import_partner_id)
            if import_partner.state == 'confirm':
                raise osv.except_osv(_('Error!'), _('Is alredy confirmed. It can not be imported from file.'))
            decoded_file_contents = base64.decodestring(distwin_wizard.file)
            try:
                unicode(decoded_file_contents, 'utf8')
            except Exception, ex: # Si no puede convertir a UTF-8 es que debe estar en ISO-8859-1: Lo convertimos
                decoded_file_contents = unicode(decoded_file_contents, 'iso-8859-1').encode('utf-8')

            for line in decoded_file_contents.split("\n"):
                fields = line.split(";")
                if fields[0] != '':
                    if fields[0] != 'codcli':
                        values = {
                            'account_number': fields[0].replace('"',''),
                            'name': fields[1].replace('"',''),
                            'address_street': fields[2].replace('"',''),
                            'address_city': fields[3].replace('"',''),
                            'address_state': fields[4].replace('"',''),
                            'address_phone': fields[9].replace('"',''),
                            'address_zip': fields[5].replace('"',''),
                            'address_country': fields[37].replace('"',''),
                            'vat_number': fields[37].replace('"','')+fields[6].replace('"',''),
                            'import_id': import_partner_id,
                        }
                        partner_line_obj.create(cr, uid, values, context=context)
        
        return {}
    
import_distwin_partner_file_wizard()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def check_vat_es(self, vat):
        return True
    
res_partner()