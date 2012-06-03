# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 NaN Projectes de Programari Lliure, S.L. All Rights Reserved
#                       http://www.NaN-tic.com
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
from osv import fields, osv
import time
import datetime
import pooler
import tools
from tools.translate import _

class project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"
        
    def _simple_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = m.name or ''
        return res
    
    _columns = {
        'simple_name': fields.function(_simple_name, method=True, string="Project Name", store=True, type='char', size=250),
    }
        
    _order = "simple_name"

project()


