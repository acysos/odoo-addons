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

class rental_agreement(osv.osv):
    _name = 'rental.agreement'
    
    def _get_mount_point(self,cr,uid,ids,name,arg,context={}):
        res = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        for top in self.browse(cr,uid,ids,context):
            if user.document_mount:
                mount = user.default_mount_agreement
            else:
                mount = company.default_mount_agreement
            if user.document_client:
                client = user.document_client
            else:
                client = company.default_document_client
            model_obj = self.pool.get('ir.model')
            model_id = model_obj.search(cr,uid,[('model','=','rental.agreement')])[0]
            dir_obj = self.pool.get('document.directory')
            dir_id = dir_obj.search(cr,uid,[('ressource_type_id','=',model_id),('domain','=','[]')])[0]
            diry = dir_obj.browse(cr,uid,dir_id,context)
            path = ''
            if client == 'unix':
                path = mount + diry.name + '/' + top.name + '/'
            elif client == 'win':
                path = mount + diry.name + '\\' + top.name + '\\'
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
                path = 'ftp://%s@%s'%(user.login, url) + '/' + diry.name + '/' + top.name + '/'
            res[top.id] = path
        return res
    
    _columns = {
        'name': fields.char('Reference', size=64, select=True, readonly=True),
        'partner_id': fields.many2one('res.partner',
            'Tenant',
            select=True,
            required=True,
            domain= [('real_state_type','=','tenant')]),
        'signing_date': fields.date('Signing date'),
        'start_date': fields.date('Start date', required=True),
        'end_date': fields.date('End date', required=True),
        'rent_price': fields.float('Rent Price'),
        'notes': fields.text('Notes'),
        'top_id': fields.many2one('real.state.top', 'Top', required=True, ondelete='cascade', select=True),
        'owner_id': fields.many2one('res.partner',
            'Owner',
            select=True,
            domain= [('real_state_type','=','owner')]),
        'rent_attachments_url': fields.function(_get_mount_point, method=True, store=False, type='char', size=1024, string='Attachments URL'),
    }
    _order = 'start_date'
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'rental.agreement')
        res = super(rental_agreement, self).create(cr, uid, vals, context)
        return res
    
    def onchange_top_id(self, cr, uid, ids, top_id):
        if not top_id:
            return {}
        top = self.pool.get('real.state.top').browse(cr,uid,top_id)
        value = {'owner_id':top.partner_id.id}
        
        return {'value': value }
    
rental_agreement()