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
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class timesheet_later(osv.osv_memory):
    _name = "timesheet.later"
    _description = "Punctuality Control"
    _inherit = "ir.wizard.screen"
    
    _columns = {
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date'),
    }
    
    def open_project_work(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        task_worj_obj = self.pool.get('project.task.work')
        employee_obj = self.pool.get('hr.employee')
        employees = employee_obj.search(cr, uid, [('active','=',True)], context=context)
        pr_task_ids = []
        for employee_id in employees:
            employee = employee_obj.browse(cr, uid, [employee_id], context)[0]
            if employee.user_id:
                start_date = datetime.strptime(data['start_date'],'%Y-%m-%d')
                if not data['end_date']:
                    end_date = datetime.strptime(time.strftime('%Y-%m-%d'),'%Y-%m-%d')
                else:
                    end_date = datetime.strptime(data['end_date'],'%Y-%m-%d')
                while start_date <= end_date:
                    t1_works = task_worj_obj.search(cr,uid,[('user_id','=',employee.user_id.id),('start_date','>',start_date.strftime('%Y-%m-%d')+' 6:00'),('start_date','<',start_date.strftime('%Y-%m-%d')+' 13:30')],order='start_date')
                    if t1_works:
                        task_work_time = datetime.strptime(task_worj_obj.browse(cr,uid,[t1_works[0]],context=context)[0].start_date,'%Y-%m-%d %H:%M:%S')
                        if task_work_time.hour >= 8 and task_work_time.minute >= 1:
                            pr_task_ids.append(t1_works[0])
                            
                    t2_works = task_worj_obj.search(cr,uid,[('user_id','=',employee.user_id.id),('start_date','>',start_date.strftime('%Y-%m-%d')+' 14:00'),('start_date','<',start_date.strftime('%Y-%m-%d')+' 20:30')],order='start_date')
                    if t2_works:
                        task_work_time = datetime.strptime(task_worj_obj.browse(cr,uid,[t2_works[0]],context=context)[0].start_date,'%Y-%m-%d %H:%M:%S')
                        if task_work_time.hour >= 15 and task_work_time.minute >= 1:
                            pr_task_ids.append(t2_works[0])
                    start_date = start_date + relativedelta(months=+0, days=+1)
        res = {
            'domain': str([('id','in',pr_task_ids)]),
            'context': str({'group_by':['user_id']}),
            'name': 'Punctuality Control',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.task.work',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res
    
timesheet_later()