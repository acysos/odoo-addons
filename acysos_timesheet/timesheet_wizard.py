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
from tools.translate import _
import netsvc
import datetime
import time
from datetime import date, timedelta

                  
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

class project_task_user_active(osv.osv):
    _name = 'project.task.user.active'
    _columns = {
        'name': fields.char('Name', size=64, readonly=False, required=True, select=True),
        'task_id': fields.many2one('project.task', 'Task', String='Task'),
        'user_id': fields.many2one('res.users', 'User', String='User'),
        'timestamp': fields.datetime('Start Time', readonly=True, help='Date and time when the task was started.'),
               }
               
    _defaults = {
        'name': lambda *a: '/',
    }
               
project_task_user_active()

class project_task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'active_user_ids': fields.one2many('project.task.user.active','task_id','Active Users'),
    }

    def create_active_user(self, cr, uid, ids, context):
        if context and 'user_id' in context:
            user = context['user_id']
        else:
            return False

        obj = self.browse(cr, uid, ids, context) 
        if type(ids) == list:
            list_obj = obj 
        else:
            list_obj = [ obj ] 

        for task_ids in list_obj:
            #If exist another active user line with this user, close
            self.pool.get('project.task.list.wizard').close_user_task(cr, uid, ids , user, context)
            self.remove_active_user(cr, uid, ids,0, context)
            #create a new task_user_active
            res = self.pool.get('project.task.user.active').create(cr, uid, {
                'task_id': task_ids.id,
                'user_id': user,
                'timestamp': datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
            }, context)


    def remove_active_user(self, cr, uid, ids, user_id, context):
        """
        Removes active_users in context, if there is no user_id in context, removes all active_users 
        """
        remove_user=[]
        if user_id == 0:
            if context and 'user_id' in context:
                remove_user = [ context['user_id'] ]
        else:
            remove_user = [user_id]
        
        obj = self.browse(cr, uid, ids, context) 
        if type(ids) == list:
            list_obj = obj 
        else:
            list_obj = [ obj ] 

        for task_id in list_obj:
            for active_user_task in task_id.active_user_ids:
                if len(remove_user) == 0 or len(remove_user) > 0 and active_user_task.user_id.id in remove_user :
                    res = self.pool.get('project.task.user.active').unlink(cr, uid, active_user_task.id )

    def do_open(self, cr, uid, ids, context):
        result = super(project_task, self).do_open(cr, uid, ids, context)
        time = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        self.create_active_user(cr, uid, ids, context)
        return result

    def do_close_timesheet(self, cr, uid, ids, user_id, context):
        result = []
        self.remove_active_user(cr, uid, ids,user_id, context)
        #if there is any active_user, it can't be closed
        if type(ids) == list:
            for task in self.browse(cr,uid,ids,context=context):
                if task.active_user_ids == None or len(task.active_user_ids) == 0:
                    result.append(super(project_task, self).do_close(cr, uid, ids, context))
        else:
            if self.browse(cr,uid,ids,context=context).active_user_ids == None:
                result = super(project_task, self).do_close(cr, uid, ids, context)

        return result

    def do_reopen(self, cr, uid, ids, context):
        result = super(project_task, self).do_reopen(cr, uid, ids, context)
        self.create_active_user(cr, uid, ids, context)
        return result

    def do_cancel(self, cr, uid, ids, context):
        self.remove_active_user(cr, uid, ids,0, context)
        result = super(project_task, self).do_cancel(cr, uid, ids, context)
        return result

    def do_draft(self, cr, uid, ids, context):
        self.remove_active_user(cr, uid, ids,0, context)
        result = super(project_task, self).do_draft(cr, uid, ids, context)
        return result

project_task()

class project_task_wizard_user( osv.osv_memory ):
    _name = 'project.task.wizard.user'
        
    _columns = {
        'user_id': fields.many2one('res.users', string='User', required=True),
        'active_user_ids': fields.many2one('project.task.user.active', string='Active Users', required=False),
    }

    def on_accept(self, cr, uid, ids, context):
        # Call another wizard
        wizard= self.browse(cr, uid, ids[0], context)
        context['user_id'] = wizard.user_id.id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'project.task.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def on_cancel(self, cr, uid, ids, context):
        return {}

    def on_close(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context)
        self.pool.get('project.task.list.wizard').close_user_tasks(cr, uid, wizard.user_id.id, context)

        # Reopen the same wizard step so information is cleared
        ctx = context.copy()
        if 'pro_id' in ctx:
            del ctx['pro_id']
        if 'user_id' in ctx:
            del ctx['user_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'project.task.wizard.user',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

project_task_wizard_user()

class project_task_wizard( osv.osv_memory ):
    _name = 'project.task.wizard'
        
    _columns = {
        'project_id': fields.many2one('project.project', string='Project'),
    }

    def on_accept(self, cr, uid, ids, context):
        # Call another wizard
        wizard= self.browse(cr, uid, ids[0], context)
        context['pro_id'] = wizard.project_id and wizard.project_id.id or False
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'project.task.list.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def on_cancel(self, cr, uid, ids, context):
        return {}

    def action_back(self,cr,uid,ids,context):
        ctx = context.copy()
        if 'pro_id' in ctx:
            del ctx['pro_id']
        if 'user_id' in ctx:
            del ctx['user_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'project.task.wizard.user',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
        
project_task_wizard()

class project_task_list_wizard( osv.osv_memory ):
    _name = 'project.task.list.wizard'
        
    _columns = {
        'task_id': fields.many2one('project.task', 'Delegated Tasks'),
    }

    def fields_get(self, cr, uid, fields=None, context=None, read_access=True):
        result = super(project_task_list_wizard, self).fields_get(cr, uid, fields, context, read_access)
        print context
        if 'pro_id' in context:
            result['task_id']['domain'] = [('project_id','=', context['pro_id'])]

        return result

    def close_user_task(self, cr, uid, task_id, user_id, context):
        """
        Close task_id for user_id
        """
        for task in self.pool.get('project.task').browse(cr, uid, task_id, context):
            end = datetime.datetime.now()
            for active_user in task.active_user_ids:
                if active_user.timestamp and active_user.user_id.id == user_id:
                    start = datetime.datetime.strptime(active_user.timestamp, TIMESTAMP_FORMAT)
                    hours = (end - start).seconds / 3600.0
                    start_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.mktime(time.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))-(hours*3600)))
                    self.pool.get('project.task.work').create(cr, uid, {
                        'name': _('Inserted by acysos_timesheet module'),
                        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'start_date':start_date,
                        'task_id': task.id,
                        'hours': hours,
                        'user_id': active_user.user_id.id,
                    }, context)

    def _search_tasks_with_active_user(self,cr,uid, user_id, context):
        """
        Search tasks with active users = user_id and state of task = open
        """

        #search active users
        active_user_list = self.pool.get('project.task.user.active').search(cr, uid, [
             ('user_id','=',user_id),
        ], context=context)

        #search tasks with active_users
        task_list=[]
        for active_user in self.pool.get('project.task.user.active').browse(cr, uid, active_user_list, context):
            if active_user.task_id and active_user.task_id.id not in task_list:
                task_list.append(active_user.task_id.id) 
        
        #tasks with active user = user_id on state = open
        result=[]
        for task in self.pool.get('project.task').browse(cr, uid, task_list, context):
            if task.state == 'open' and task.id not in result:
                result.append(task.id)

        return result

    def close_user_tasks(self, cr, uid, user_id, context):
        #if 'user_id' not in context:
            #context.update({'user_id':user_id})
        task_ids = self._search_tasks_with_active_user(cr, uid, user_id, context)

        if not task_ids:
            return

        for task in self.pool.get('project.task').browse(cr, uid, task_ids, context):
            self.close_user_task(cr, uid, [ task.id ], user_id, context)
            self.pool.get('project.task').do_close_timesheet(cr, uid, [ task.id ],user_id, context)

    def action_start(self, cr, uid, ids, context):
        """
        Create service with action named 'input register' and with current date
        """
        if context is None:
            context = {}

        if not 'user_id' in context:
            return {}

        self.close_user_tasks(cr, uid, context['user_id'], context)

        for task in [ x.task_id for x in self.browse(cr, uid, ids, context) ]:
            if task.state == 'open':
                #new functionality
                self.pool.get('project.task').do_reopen(cr, uid, [task.id], context)
                #return {}
            else:
                self.pool.get('project.task').do_open(cr, uid, [task.id], context)

        ctx = context.copy()
        if 'pro_id' in ctx:
            del ctx['pro_id']
        if 'user_id' in ctx:
            del ctx['user_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'project.task.wizard.user',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def action_close(self,cr,uid,ids,context):
        """
        Close task of current user
        """
        if context is None:
            context = {}

        if not 'user_id' in context:
            return {}

        task_ids = [ x.task_id.id for x in self.browse(cr, uid, ids, context) if x.task_id ]
        if task_ids:
            self.close_user_task(cr, uid, task_ids, context['user_id'], context)
            self.pool.get('project.task').do_close_timesheet(cr, uid, task_ids,context['user_id'], context)

        ctx = context.copy()
        if 'pro_id' in ctx:
            del ctx['pro_id']
        if 'user_id' in ctx:
            del ctx['user_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'project.task.wizard.user',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def action_back(self,cr,uid,ids,context):
        ctx = context.copy()
        if 'pro_id' in ctx:
            del ctx['pro_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'project.task.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

project_task_list_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
