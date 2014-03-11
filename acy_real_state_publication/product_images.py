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
from osv import osv, fields
import base64, urllib
from ftplib import FTP
import os

class product_images(osv.osv):
    _inherit = "product.images"
    
    _columns = {
        'top_id':fields.many2one('real.state.top', 'Top'),
        'sequence': fields.integer('Sequence', required=True),
    }
    
    _order = 'sequence asc' 
    
    def _delete_from_ftp_server(self,cr,uid,image,company,top,context):
        ftp = FTP(company.ftp_host)
        if company.ftp_anonymous:
            ftp.login()
        else:
            ftp.login(company.ftp_user, company.ftp_password or '')
        if company.ftp_folder:
            ftp.cwd(company.ftp_folder+top.name)
        try:
            ftp.delete(image.name)
        except Exception, e:
            print e
        return True
        
    def _delete_file(self,cr,uid,image,company,top,context):
        path = company.local_media_repository+top.name+'/'+image.name
        if os.path.exists(path):
            os.remove(path)
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        for id in ids:
            image = self.browse(cr,uid,id,context)
            if company.ftp_host:
                self._delete_from_ftp_server(cr,uid,image,company,image.top_id,context)
            self._delete_file(cr,uid,image,company,image.top_id,context)
        
        return super(product_images, self).unlink(cr, uid, ids, context=context)
    
product_images()