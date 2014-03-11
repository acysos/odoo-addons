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

from osv import fields,osv
from tools.translate import _

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def _get_mount_point(self,cr,uid,ids,name,arg,context={}):
        res = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        for partner in self.browse(cr,uid,ids,context):
            if user.document_mount:
                mount = user.default_mount_agreement
            else:
                mount = company.default_mount_agreement
            if user.document_client:
                client = user.document_client
            else:
                client = company.default_document_client
            model_obj = self.pool.get('ir.model')
            model_id = model_obj.search(cr,uid,[('model','=','res.partner')])[0]
            dir_obj = self.pool.get('document.directory')
            dir_id = dir_obj.search(cr,uid,[('ressource_type_id','=',model_id)])[0]
            diry = dir_obj.browse(cr,uid,dir_id,context)
            path = ''
            if client == 'unix':
                path = mount + diry.name + '/' + partner.ref + '/'
            elif client == 'win':
                path = mount + diry.name + '\\' + partner.ref + '\\'
            elif client == 'web':
                data_pool = self.pool.get('ir.model.data')
                aid = data_pool._get_id(cr, uid, 'document_ftp', 'action_document_browse')
                aid = data_pool.browse(cr, uid, aid, context=context).res_id
                ftp_url = self.pool.get('ir.actions.url').browse(cr, uid, aid, context=context)
                url = ftp_url.url and ftp_url.url.split('ftp://') or []
                if url:
                    url = url[1]
                    if url[-1] == '/':
                        url = url[:-1]
                else:
                    url = '%s:%s' %(ftpserver.HOST, ftpserver.PORT)
                path = 'ftp://%s@%s'%(user.login, url) + '/' + diry.name + '/' + partner.ref + '/'
            res[partner.id] = path
        return res
    
    _columns = {
        'name2': fields.char('Second Owner', size=128, required=False, select=True),
        'vat2': fields.char('Second VAT',size=32 ),
        'real_state_type': fields.selection([('owner','Owner'),
                                ('tenant','Tenant'),
                                ('buyer','Buyer'),
                                ('manage','Manage')], 'Type', required=True, select=True),
        'partner_attachments_url': fields.function(_get_mount_point, 
            method=True, store=False, type='char', size=1024, 
            string='Attachments URL'),
    }
    
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        if context.get('show_ref', False):
            rec_name = 'ref'
        else:
            rec_name = 'name'
        res = []
        for r in self.read(cr, uid, ids, [rec_name,'name2'], context):
            if rec_name == 'ref':
                res.append((r['id'], r[rec_name]))
            else:
                name = r[rec_name]
                if r['name2'] != False:
                    name +=' - '+r['name2']
                res.append((r['id'], name))
        return res
    
res_partner()

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    
    _columns = {
        'vat': fields.char('VAT',size=32 ),
    }
    
    _defaults = {
        'vat': lambda self, cr, uid, context : context['vat'] if context and 'vat' in context else None,
        'name': lambda self, cr, uid, context : context['name'] if context and 'name' in context else None,
    }
    
    _order = 'id ASC'
    
res_partner_address()