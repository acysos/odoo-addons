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

import os
import base64
import Image

from osv import fields, osv
from tools.translate import _
from ftplib import FTP

class LoadProductMedia(osv.osv_memory):
    _inherit = "load.product.media"
    
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
    }
    
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
        
        image = Image.open(directory+'/'+filename)
        width, height = image.size
        
        if width > company.image_width or height > company.image_height:
            if width >= height:
                ratio = float(height)/float(width)
                new_width = company.image_width
                new_height = int(new_width * ratio)
            elif height >= width:
                ratio = float(width)/float(height)
                new_height = company.image_height
                new_width = int(new_height * ratio)
        else:        
            new_width = width
            new_height = height
        image2 = image.resize((new_width, new_height), Image.ANTIALIAS)  
        image2.save(directory+'/'+filename)
        
        file = open(directory+'/'+filename, 'rb')
        ftp.storbinary('STOR %s' % filename, file)
        file.close()
        return True
    
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
    
    def load_media(self, cr, uid, data, context=None):
        """Load and create a product image """
        if context == None:
            raise osv.except_osv(_('Error!'), _('Context is missing !'))

        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        if not company.local_media_repository:
            raise osv.except_osv(_('Error!'), _('The path to OpenERP medias folder is not configured on the company !'))

        media = self.browse(cr, uid, data[0], context).media or False
        sequence = self.browse(cr, uid, data[0], context).sequence or False
        if not media:
            raise osv.except_osv(_('Error!'), _('No media selected !'))
        filename = self.browse(cr, uid, data[0], context).media_fname or False
        if not filename:
            raise osv.except_osv(_('Error!'), _('No filename !'))
        
        if 'top_id' in context:
            top = self.pool.get('real.state.top').browse(cr,uid,context['top_id'],context)
            directory = company.local_media_repository+top.name
        else:
            directory = company.local_media_repository
        self._save_file(directory, filename, media)
        
        if 'top_id' in context:
            data = {'filename': company.url_media_repository+top.name+'/'+filename,
                'link': True,'sequence':sequence}
            if company.ftp_host:
                self._upload_to_ftp_server(cr,uid, company, top, filename, context)
        else:
            data = {'filename': filename,
                'link': True,}
        
        if context['create']:
            if 'product_id' in context:
                data.update({'name': filename,
                            'product_id': context['product_id']})
            if 'top_id' in context:
                data.update({'name': filename,
                            'top_id': context['top_id']})
            self._create_image(cr, uid, data, context)
        else:
            self._update_image(cr, uid, data, context)

        return {'type':'ir.actions.act_window_close'}
    
LoadProductMedia()