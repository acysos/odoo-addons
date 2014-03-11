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
import base64
import os
from ftplib import FTP
import magic

class real_state_top_press_publication(osv.osv):
    _name = 'real.state.top.press.publication'
    
    _columns = {
        'date': fields.date('Date', required=True),
        'page': fields.integer('Page'),
        'press_id': fields.many2one('res.partner', 'Press', ondelete='cascade'),
    }
    _order = 'date'
real_state_top_press_publication()

class real_state_top_press(osv.osv):
    _name = 'real.state.top.press'
    _columns = {
        'name': fields.char('Press', required=True, size=64),
        'actual': fields.boolean('Active'),
        'date_publications': fields.one2many('real.state.top.press.publication','press_id','Date Publications'),
        'top_id': fields.many2one('real.state.top', 'Top', ondelete='cascade'),
    }
    _order = 'name'
    
    _defaults = {
        'actual': lambda *a: 1,
    }
    
real_state_top_press()

class real_state_top_internet_wo(osv.osv):
    _name = 'real.state.top.internet.wo'
    _columns = {
        'name': fields.char('Website', required=True, size=64),
        'actual': fields.boolean('Active'),
        'top_id': fields.many2one('real.state.top', 'Top', ondelete='cascade'),
    }
    _order = 'name'
    
    _defaults = {
        'actual': lambda *a: 1,
    }
    
real_state_top_internet_wo()

class real_state_top(osv.osv):
    _inherit = 'real.state.top'
    
    _columns = {
        'publications': fields.one2many('real.state.top.press','top_id','Publications'),
        'internet_wo': fields.one2many('real.state.top.internet.wo','top_id','Internet WO Update'),
        'poster': fields.boolean('Poster'),
        'internet_description': fields.text('Internet Description'),
        'image_ids':fields.one2many(
                'product.images',
                'top_id',
                'Top Images'
        ),
        'energy_doc_url': fields.char('Energy URL', size=512),
    }
    
    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(path):
            raise osv.except_osv(_('Error!'), _('The path to OpenERP medias folder does not exists on the server !'))        
        
        full_path = os.path.join(path, filename)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True
    
    def _upload_to_ftp_server(self, cr, uid, company, top, filename, context):
        directory = company.local_media_repository+top.name
        ftp = FTP(company.ftp_host)
        if company.ftp_anonymous:
            ftp.login()
        else:
            ftp.login(company.ftp_user, company.ftp_password or '')
        if company.ftp_folder:
            try:
                ftp.mkd(company.ftp_folder+top.name)
            except Exception, e:
                print e
            ftp.cwd(company.ftp_folder+top.name)
        filetype = magic.from_file(directory+'/'+filename, mime=True)
        if filetype != 'application/pdf':
            raise osv.except_osv(_('Error!'), 
                         _('The certificate file should be a PDF File'))
         
        file = open(directory+'/'+filename, 'rb')
        ftp.storbinary('STOR %s' % filename, file)
        file.close()
        return True
    
    def _delete_file(self, cr, uid, company, top, filename, context):
        path = company.local_media_repository+top.name+'/'+filename
        if os.path.exists(path):
            os.remove(path)
        return True
    
    def _delete_from_ftp_server(self, cr, uid, company, top, 
                                filename, context):
        ftp = FTP(company.ftp_host)
        if company.ftp_anonymous:
            ftp.login()
        else:
            ftp.login(company.ftp_user, company.ftp_password or '')
        if company.ftp_folder:
            ftp.cwd(company.ftp_folder+top.name)
        try:
            ftp.delete(filename)
        except Exception, e:
            print e
        return True
    
    def create(self, cr, uid, vals, context=None):
        res = super(real_state_top, self).create(cr, uid, vals, context)
        if 'energy_doc' in vals:
            user = self.pool.get('res.users').browse(cr, uid, uid)
            company = user.company_id
            top = self.browse(cr,uid,res,context)
            directory = company.local_media_repository+top.name
            filename = _('certificate_%s.pdf')%(top.name)
            if vals['energy_doc'] != False:
                self._save_file(directory, filename, vals['energy_doc'])
                if company.ftp_host:
                    self._upload_to_ftp_server(cr,uid, company, top, 
                                               filename, context)
                    energy_doc_url = company.url_media_repository+top.name+'/'+filename
                    self.write(cr,uid,res,{'energy_doc_url' : energy_doc_url},
                               context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'energy_doc' in vals:
            for top_id in ids:
                user = self.pool.get('res.users').browse(cr, uid, uid)
                company = user.company_id
                top = self.browse(cr,uid,top_id,context)
                directory = company.local_media_repository+top.name
                filename = _('certificate_%s.pdf')%(top.name)
                if vals['energy_doc'] != False:
                    self._save_file(directory, filename, vals['energy_doc'])
                    if company.ftp_host:
                        self._upload_to_ftp_server(cr,uid, company, top, 
                                                   filename, context)
                        vals['energy_doc_url'] = company.url_media_repository+top.name+'/'+filename
                elif vals['energy_doc'] == False:
                    vals['energy_doc_url'] = False
                    self._delete_file(cr, uid, company, top, filename, context)
                    if company.ftp_host:
                        self._delete_from_ftp_server(cr, uid, company, top, 
                                                     filename, context)
                
        res = super(real_state_top, self).write(cr, uid, ids, vals, context)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        for top_id in ids:
            top = self.browse(cr,uid,top_id,context)
            directory = company.local_media_repository+top.name
            filename = _('certificate_%s.pdf')%(top.name)
            if company.ftp_host:
                self._delete_from_ftp_server(cr, uid, company, top, 
                                             filename, context)
            self._delete_file(cr, uid, company, top, filename, context)
        
        return super(real_state_top, self).unlink(cr, uid, ids, context=context)
    
real_state_top()