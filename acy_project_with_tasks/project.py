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

from lxml import etree
import time
from datetime import datetime, date

from tools.translate import _
from osv import fields, osv

class task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'project_id': fields.many2one('project.project', 'Project', select=True, ondelete='cascade', help="If you have [?] in the project name, it means there are no analytic account linked to this project."),
        'partner_id': fields.related('project_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
    }
task()

class project_work(osv.osv):
    _inherit = "project.task.work"
    
    _columns = {
        'start_date': fields.datetime('Starting Date'),
        'negative_reason': fields.text('Negative Reason'),
    }
    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': lambda *a: '/',
    }
    
    def _update_estimate_hours(self,cr,uid,ids,context={}):

        task = self.browse(cr, uid, ids, context)[0].task_id
        task_works = self.search(cr, uid, [('task_id','=',task.id)], context=context)
        worked_hours = 0
        for work in self.browse(cr, uid, task_works, context):
            worked_hours += work.hours
            
        self.pool.get('project.task').write(cr,uid,[task.id],{'effective_hours':worked_hours})

        return True
    
    def create(self, cr, uid, vals, *args, **kwargs):
        if 'hours' in vals and (not vals['hours']):
            vals['hours'] = 0.00
        if 'task_id' in vals:
            cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s', (vals.get('hours',0.0), vals['task_id']))
        work = super(project_work,self).create(cr, uid, vals, *args, **kwargs)
        self._update_estimate_hours(cr,uid,[work])
        return work
    
    def hours_change(self, cr, uid, ids,date,start_date,hours,user_id):
        res={}
        res['value']={}
        res['value']['user_id']=user_id
        if hours >= 0:
            if date and start_date:
                res['value']['date']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.mktime(time.strptime(start_date, '%Y-%m-%d %H:%M:%S'))+(hours*3600)))
                if ids: self.write(cr,uid,ids,{'date':res['value']['date'],'hours':hours,'user_id':user_id})
            if not date:
                res['value']['date']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.mktime(time.strptime(start_date, '%Y-%m-%d %H:%M:%S'))+(hours*3600)))
                if ids: self.write(cr,uid,ids,{'date':res['value']['date'],'hours':hours,'user_id':user_id})
            if not start_date:
                res['value']['start_date']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S'))-(hours*3600)))
                if ids: self.write(cr,uid,ids,{'start_date':res['value']['start_date'],'hours':hours,'user_id':user_id})
        else:
            res['value']['date'] = date
            res['value']['start_date'] = start_date
        if ids: self._update_estimate_hours(cr,uid,ids)
        return res
        
    def date_change(self, cr, uid, ids,date,start_date,user_id):
        res={}
        res['value']={}
        res['value']['user_id']=user_id
        if date and start_date:
            if start_date > date:
                raise osv.except_osv(_('Error !'), _('The start date must be before the end date !'))
            else: 
                res['value']['hours']= (time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S'))-time.mktime(time.strptime(start_date, '%Y-%m-%d %H:%M:%S')))/3600
                if ids: self.write(cr,uid,ids,{'date':date,'start_date':start_date,'hours':res['value']['hours'],'user_id':user_id})
        if ids: self._update_estimate_hours(cr,uid,ids)
        return res
            
project_work()

class project_task_work_update_start_date(osv.osv_memory):
    """
    Wizard to update the start date
    """

    _name = 'project.task.work.update.start.date'

    def action_update(self, cr, uid, ids, context=None):
        cr.execute('select project_task_work.id,project_task_work.date,project_task_work.hours from project_task_work')
        rows = cr.fetchall()
        for row in rows:
            start_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.mktime(time.strptime(row[1], '%Y-%m-%d %H:%M:%S'))-(row[2]*3600)))
            sql = "update project_task_work set start_date= '%s' where id= %i " % (start_date,row[0])
            cr.execute(sql)
        return {}

project_task_work_update_start_date()