# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#                       Daniel Pascal <daniel@acysos.com>
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

from openerp import models, fields, api, _
import platform

class res_partner(models.Model):
    _inherit = "res.partner"
    
    
    '''
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
    ''' 
    
    #prueba

    @api.multi
    def _get_mount_point(self):
        user = self.env.user
        company = user.company_id
        for partner in self:
            if user.document_mount:
                mount = user.default_mount_agreement
            else:
                mount = company.default_mount_agreement
            if user.document_client:
                client = user.document_client
            else:
                client = company.default_document_client
            model_id = self.env['ir.model'].search([('model','=',
                                                     'res.partner')])
            dir_obj = self.env['document.directory']
            dir_id = dir_obj.search([('ressource_type_id','=',model_id.id)])
            print mount
            print dir_id.name
            print partner.ref
            path = ''
            if client == 'unix':
                path = mount + dir_id.name + '/' + partner.ref + '/'
            elif client == 'win':
                path = mount + dir_id.name + '\\' + partner.ref + '\\'
            partner.partner_attachments_url = path
        

    
    name2 = fields.Char('Second Owner', size=128, required=False, 
                        select=True)
    vat2 = fields.Char('Second VAT',size=32 )
    real_state_type = fields.Selection([('owner','Owner'),
                                ('tenant','Tenant'),
                                ('buyer','Buyer'),
                                ('manage','Manage')], 'Type', required=True, 
                                       select=True)
    
    partner_attachments_url = fields.Char(compute='_get_mount_point', 
                                          store=False, size=1024, 
                                          string='Attachments URL')
    
    
