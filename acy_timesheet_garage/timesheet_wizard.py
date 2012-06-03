# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import tools
import os

class project_task_user_active(osv.osv):
    _inherit = 'project.task.user.active'
    
    def _project_name_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for user_active in self.browse(cr,uid,ids,context):
            if user_active.task_id.project_id: res[user_active.id] = user_active.task_id.project_id.name
            else: res[user_active.id] = ''
        return res
            
    def _trademark_model_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for user_active in self.browse(cr,uid,ids,context):
            if user_active.task_id.project_id: res[user_active.id] = user_active.task_id.project_id.trademark_model
            else: res[user_active.id] = ''
        return res
            
    def _vehicle_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for user_active in self.browse(cr,uid,ids,context):
            if user_active.task_id.vehicle_id: res[user_active.id] = user_active.task_id.vehicle_id.name
            else: res[user_active.id] = ''
        return res
    
    _columns = {
        'project_name': fields.function(_project_name_get, method=True, store=True, type='char', size=64, string='Project', readonly=True),
        'trademark_model': fields.function(_trademark_model_get, method=True, store=True, type='char', size=64, string='Trademark + Model', readonly=True),
        'vehicle': fields.function(_vehicle_get, method=True, store=True, type='char', size=64, string='Vehicle', readonly=True),
    }
    
project_task_user_active()
