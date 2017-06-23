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

class rental_agreement(models.Model):
    _name = 'rental.agreement'
    
    '''def _get_mount_point(self,cr,uid,ids,name,arg,context={}):
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
    '''
    
    @api.multi
    def _get_mount_point(self):
        user = self.env.user
        print user
        company = user.company_id
        print company
        for top in self:
            if user.document_mount:
                mount = user.default_mount_agreement
                print mount
            else:
                mount = company.default_mount_agreement
                print mount
            if user.document_client:
                client = user.document_client
                print client
            else:
                client = company.default_document_client
                print client
            model_id = self.env['ir.model'].search([('model','=',
                                                     'real.state.top')])
            print model_id
            dir_obj = self.env['document.directory']
            dir_id = dir_obj.search([('ressource_type_id','=',model_id.id),
                                     ('domain','=','[]')])
            print dir_id.name
            print top.name
            path = ''
            if client == 'unix':
                path = mount + 'Real_State' + '/' + top.name + '/'
            elif client == 'win':
                path = mount + 'Real_State' + '\\' + top.name + '\\'
            top.rent_attachments_url = path
    
    
    name = fields.Char('Reference', size=64, select=True, readonly=True)
    partner_id = fields.Many2one('res.partner',
        'Tenant',
        select=True,
        required=True,
        domain= [('real_state_type','=','tenant')])
    signing_date = fields.Date('Signing date')
    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date', required=True)
    rent_price = fields.Float('Rent Price')
    notes = fields.Text('Notes')
    top_id = fields.Many2one('real.state.top', 'Top', required=True, 
                             ondelete='cascade', select=True)
    owner_id = fields.Many2one('res.partner',
        'Owner',
        select=True,
        domain= [('real_state_type','=','owner')])
    rent_attachments_url = fields.Char(compute='_get_mount_point', store=False, 
                                       string='Attachments URL')
    
    _order = 'start_date'
    
    @api.onchange('top_id')
    def onchange_top_id(self):
        if self.top_id:
            owner_id = self.top_id.partner_id
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('rental.agreement')
        res = super(rental_agreement, self).create(vals)
        return res
        
        
        
    
    
    