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

class res_users(models.Model):
    _inherit = "res.users"
    _name = "res.users"
    document_mount = fields.Char('Document Mount',size=256,
                                 help='Local mount point')
    default_mount_agreement = fields.Char('Default Mount Rental Agreement',
                                    size=256,
                                    help='Local mount point for rental agreement')
    document_client = fields.Selection([('win','Windows Client'),
                                ('unix','Linux/MacOSX Client'),
                                ('web','Web Client')], 'Client')
    
    
    
    
    