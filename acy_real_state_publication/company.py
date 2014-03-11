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

class res_company(osv.osv): 
    _inherit = "res.company"
    _columns = {
        'ftp_host':fields.char('FTP Host',size=256,help='Remote ftp host'),
        'ftp_anonymous': fields.boolean('FTP Anonymous'),
        'ftp_user':fields.char('FTP User',size=256),
        'ftp_password':fields.char('FTP Password',size=256),
        'ftp_folder':fields.char('FTP Folder',size=256),
        'image_width': fields.integer('Image Width'),
        'image_height': fields.integer('Image Height')  
    }
res_company()