# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

class project(osv.osv):
    _inherit = 'project.project'
    
    def _trademark_model_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for project in self.browse(cr,uid,ids,context):
            if project.vehicle_id: res[project.id] = project.vehicle_id.trademark_id.name +'-'+ project.vehicle_id.model_id.name
            else: res[project.id] = ''
        return res
    
    _columns = {
        'vehicle_id': fields.many2one('res.partner.vehicle', 'Vehicle', readonly=True, states={'open': [('readonly', False)]}, required=False),
        'trademark_model': fields.function(_trademark_model_get, method=True, store=True, type='char', size=64, string='Trademark + Model', readonly=True),
    }
project()

class task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'vehicle_id': fields.related('project_id', 'vehicle_id', type='many2one', relation='res.partner.vehicle', string='Vehicle'),
    }
task()

class project_work(osv.osv):
    _inherit = "project.task.work"
    
    def _trademark_model_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for work in self.browse(cr,uid,ids,context):
            if work.task_id.vehicle_id: res[work.id] = work.task_id.vehicle_id.trademark_id.name +'-'+ work.task_id.vehicle_id.model_id.name
            else: res[work.id] = ''
        return res
        
    def _vehicle_get(self,cr,uid,ids,name,arg,context={}):
        res={}
        for work in self.browse(cr,uid,ids,context):
            if work.task_id.vehicle_id: res[work.id] = work.task_id.vehicle_id.name
            else: res[work.id] = ''
        return res
    
    _columns = {
        'vehicle': fields.function(_vehicle_get, method=True, store=True, type='char', size=64, string='Vehicle', readonly=True),
        'trademark_model': fields.function(_trademark_model_get, method=True, store=True, type='char', size=64, string='Trademark + Model', readonly=True),
    }
    
project_work()