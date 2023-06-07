# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
from odoo.tools import float_compare
import base64
import io
from odoo.addons.resource.models.resource import HOURS_PER_DAY


hour_list = [('0', '00:00'), ('0.5', '00:30'),
            ('1', '01:00'), ('1.5', '01:30'),
            ('2', '02:00'), ('2.5', '02:30'),
            ('3', '03:00'), ('3.5', '03:30'),
            ('4', '04:00'), ('4.5', '04:30'),
            ('5', '05:00'), ('5.5', '05:30'),
            ('6', '06:00'), ('6.5', '06:30'),
            ('7', '07:00'), ('7.5', '07:30'),
            ('8', '08:00'), ('8.5', '08:30'),
            ('9', '09:00'), ('9.5', '09:30'),
            ('10', '10:00'), ('10.5', '10:30'),
            ('11', '11:00'), ('11.5', '11:30'),
            ('12', '12:00'), ('12.5', '12:30'),
            ('13', '13:00'), ('13.5', '13:30'),
            ('14', '14:00'), ('14.5', '14:30'),
            ('15', '15:00'), ('15.5', '15:30'),
            ('16', '16:00'), ('16.5', '16:30'),
            ('17', '17:00'), ('17.5', '17:30'),
            ('18', '18:00'), ('18.5', '18:30'),
            ('19', '19:00'), ('19.5', '19:30'),
            ('20', '20:00'), ('20.5', '20:30'),
            ('21', '21:00'), ('21.5', '21:30'),
            ('22', '22:00'), ('22.5', '22:30'),
            ('23', '23:00'), ('23.5', '23:30'),
            ('0', '--:--')]

class WebsiteHoliday(http.Controller):

    def default_start(self):
        now = datetime.now()
        return str(datetime(now.year, 1, 1))

    def default_end(self):
        now = datetime.now()
        return str(datetime(now.year, 12, 31))

    def _compute_allocation_count(self):
        for employee in self:
            allocations = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id.active', '=', True),
                ('state', '=', 'validate'),
                ])
            employee.allocation_count = sum(allocations.mapped('number_of_days'))
            employee.allocation_display = "%g" % employee.allocation_count

    @http.route(['/employee/holidays'], type='http', auth='user', website=True)
    def website_holidays(self):
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        if not emp_id:
            request.redirect('/web/login')
        holiday_types = request.env['hr.leave.type'].sudo().search(
            [('is_holyday', '=', True)])
        holidays = request.env['hr.leave'].sudo().search(
            [('employee_id', '=', emp_id.id),
             ('holiday_status_id', 'in', holiday_types.ids),
             ('request_date_from', '>=', self.default_start()),
             ('request_date_to', '<=', self.default_end())])
        allocations = request.env['hr.leave.allocation'].sudo().search([
                ('employee_id', '=', emp_id.id),
                ('holiday_status_id', 'in', holiday_types.ids),
                ('state', '=', 'validate'),
            ])
        allo_h = sum(allocations.mapped('number_of_days'))
        allo_s = allo_h
        for holi in holidays:
            allo_s -= holi.number_of_days
        values = {'holidays': holidays,
                  'allocation_display': str(int(allo_s)) + '/' + str(int(allo_h)) + ' Dias'}
        return request.render('website_holidays.website_holidays', values)

    @http.route(['/employee/leaves'], type='http', auth='user', website=True)
    def website_leave(self):
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        if not emp_id:
            request.redirect('/web/login')
        leave_types = request.env['hr.leave.type'].sudo().search(
            [('is_holyday', '=', False)])
        leaves = request.env['hr.leave'].sudo().search(
            [('employee_id', '=', emp_id.id),
             ('holiday_status_id', 'in', leave_types.ids),
             ('request_date_to', '>=', self.default_start()),
             ('request_date_to', '<=', self.default_end())])
        allocations = request.env['hr.leave.allocation'].sudo().search([
                ('employee_id', '=', emp_id.id),
                ('holiday_status_id', 'in', leave_types.ids),
                ('state', '=', 'validate'),
            ])
        allo_h = 0
        for allocation in allocations:
            if allocation.parent_id and allocation.parent_id.type_request_unit == "hour":
                allo_h += allocation.number_of_days * HOURS_PER_DAY
            else:
                allo_h += allocation.number_of_days * (
                    allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day or HOURS_PER_DAY)
        allo_s = allo_h
        # for leave in leaves:
        #     if leave.holiday_status_id.allocation_type != 'no':
        #         allo_s -= self.sudo().get_leave_hours(leave)
        values = {'holidays': leaves,
                  'allocation_display': str(int(allo_s)) + '/' + str(int(allo_h)) + ' Horas'}
        return request.render('website_holidays.website_leaves', values)

    def get_leave_hours(self, leave):
        if leave.request_unit_half:
            if len(self.resume_line) > 1:
                tot_h = 0
                for line in self.resume_line:
                    tot_h += line.work_time
                if leave.request_date_from_period == 'am':
                    return self.hours_per_leave - tot_h
                else:
                    return self.hours_per_leave - tot_h
            else:
                return self.hours_per_leave/2
        elif leave.request_unit_hours:
            return (leave.date_to - leave.date_from).total_seconds() / 3600
        else:
            return self.hours_per_leave

    @http.route('/holiday/request', type='json', auth="user", website=True)
    def holiday_request(self):
        emp = request.env.user.sudo().employee_ids[0].id if request.env.user.sudo().employee_ids else False
        timeoff_types = request.env['hr.leave.type'].with_context(
            {'employee_id': emp}).sudo().search([('is_holyday', '=', True), ('available_portal', '=', True)], order="name")
        request_unit = request.env['hr.leave.type'].sudo().search(
            [('is_holyday', '=', True)])[0].request_unit
        today = fields.Date.today()
        result = {'timeoff_types': timeoff_types,
                    'req_date_from': today,
                    'req_date_to': today,
                    'number_of_days': '1',
                    'request_unit': request_unit,
                    'request_date_from_period': [('am', 'Morning'), ('pm', 'Afternoon')],
                    'request_hour_from': hour_list,
                    'request_hour_to': hour_list,
                    'employee_id': emp,
                    'req_unit': timeoff_types[0].request_unit}
        print(result)
        return request.env['ir.ui.view']._render_template("website_holidays.leave_request", result)


    @http.route('/timeoff/request', type='json', auth="user", website=True)
    def timeoff_request(self):
        emp = request.env.user.sudo().employee_ids[0].id if request.env.user.sudo().employee_ids else False
        timeoff_types = request.env['hr.leave.type'].with_context(
            {'employee_id': emp}).sudo().search([('is_holyday', '=', False), ('available_portal', '=', True)], order="name")
        request_unit = request.env['hr.leave.type'].sudo().search([('is_holyday', '=', False)])[0].request_unit
        today = fields.Date.today()
        result = {'timeoff_types': timeoff_types,
                    'req_date_from': today,
                    'req_date_to': today,
                    'number_of_days': '1',
                    'request_unit': request_unit,
                    'request_date_from_period': [('am', 'Morning'), ('pm', 'Afternoon')],
                    'request_hour_from': hour_list,
                    'request_hour_to': hour_list,
                    'employee_id': emp,
                    'req_unit': timeoff_types[0].request_unit}
        return request.env['ir.ui.view']._render_template("website_holidays.leave_request", result)


    @http.route(['/timeoff/requests/submit'],type='json', auth="user", website=True)
    def timeoff_request_submit(self,name, request_date_from, request_date_to, 
                               duration,holiday_status_id, unit_half=False, 
                               unit_hour=False, period=False, hour_from=False,
                               hour_to=False, attach=False):
        message = ''
        print(holiday_status_id)
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        if emp_id:
            holiday_status_id = request.env['hr.leave.type'].browse(int(holiday_status_id))
            request_date_from1 = datetime.strptime(request_date_from, '%Y-%m-%d') if request_date_from != '' else False
            request_date_to1 = datetime.strptime(request_date_to, '%Y-%m-%d') if request_date_to != '' else False
            print(holiday_status_id)
            print(holiday_status_id.name)
            try:
                if holiday_status_id.request_unit == 'hour':
                    duration = 0.1
                if request_date_from1 and request_date_to1 and request_date_from1.date() > request_date_to1.date():
                    message = "The start date must be anterior to the end date."
                if duration and float(duration) <0:
                    message = "If you want to change the number of days you should use the 'period' mode"
                leave_days = holiday_status_id.sudo().get_days(emp_id.id)[holiday_status_id.id]
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    message = 'The number of remaining time off is not sufficient for this time off type.\n Please also check the time off waiting for validation.'
                domain = [
                    ('date_from', '<', request_date_to1),
                    ('date_to', '>', request_date_from1),
                    ('employee_id', '=', emp_id.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                ]
                nholidays = request.env['hr.leave'].search_count(domain)
                if nholidays:
                    message = 'You can not set 2 time off that overlaps on the same day for the same employee.'
                if message == '':
                    vals = {
                        'name': name,
                        'holiday_status_id': int(holiday_status_id),
                        'department_id': emp_id.department_id.id if emp_id and emp_id.department_id else False,
                        'employee_id': emp_id.id if emp_id else False,
                        'request_date_from': request_date_from1.date() if request_date_from1 else False,
                        'request_date_to': request_date_to1.date() if request_date_to1 else request_date_from1.date(),
                        'number_of_days': duration,
                        'state': 'confirm',
                        'request_unit_half': unit_half if unit_half != '' else False,
                        'request_date_from_period': period,
                        'request_unit_hours': holiday_status_id.request_unit == 'hour',
                        'request_hour_from': hour_from if hour_from != '' else False,
                        'request_hour_to': hour_to if hour_to != '' else False,
                        'holiday_type': 'employee',
                        }
                    res = request.env['hr.leave'].sudo().create(vals)
                    if holiday_status_id.request_unit == 'hour':
                        res.sudo()._onchange_request_parameters()
                    message = "Your timeoff request is submitted Successfully!!"
            except Exception as e:
                message = str(e)
        else:
            message = "Timeoff cannot be requested as Portal User not linked with any Employee."
        return request.env['ir.ui.view']._render_template("website_holidays.holidays_request_submit", {'message':message, 'error': {}})


    @http.route('/holidays/edit', type='json', auth="user", website=True)
    def holiday_edit(self, leave_id):
        if request.env.user.sudo().employee_ids:
            leave_id = request.env['hr.leave'].browse(int(leave_id))
            emp = request.env.user.sudo().employee_ids[0].id
            timeoff_types = request.env['hr.leave.type'].with_context(
                {'employee_id': emp}).sudo().search([('is_holyday', '=', True)])
            vals = {'leave_id': leave_id.id,
                 'request_date_from':leave_id.request_date_from.strftime('%Y-%m-%d') if leave_id.request_date_from else False,
                 'request_date_to': leave_id.request_date_to.strftime('%Y-%m-%d') if leave_id.request_date_to else False,
                 'name':leave_id.name, 'request_date_from_period':[('am', 'Morning'), ('pm', 'Afternoon')],
                 'period':leave_id.request_date_from_period,
                 'request_unit_half':leave_id.request_unit_half,
                 'request_unit_hours': leave_id.request_unit_hours,
                 'request_unit_custom': leave_id.request_unit_custom,
                 'request_hour_from':hour_list,
                 'hour_from': leave_id.request_hour_from,
                 'request_hour_to':hour_list,
                 'hour_to': leave_id.request_hour_to,
                 'number_of_days': leave_id.number_of_days,
                 'number_of_hours_display': leave_id.sudo().number_of_hours_display,
                 'employee_id': leave_id.sudo().employee_id,
                 'department_id': leave_id.department_id,
                 'holiday_status_id': leave_id.holiday_status_id,
                 'request_unit': leave_id.holiday_status_id.request_unit,
                 'timeoff_types': timeoff_types}
            return request.env['ir.ui.view']._render_template("website_holidays.holidays_edit", vals)


    @http.route('/leave/edit', type='json', auth="user", website=True)
    def leave_edit(self, leave_id):
        if request.env.user.sudo().employee_ids:
            leave_id = request.env['hr.leave'].browse(int(leave_id))
            emp = request.env.user.sudo().employee_ids[0].id
            timeoff_types = request.env['hr.leave.type'].with_context(
                {'employee_id': emp}).sudo().search([('is_holyday', '=', False)])
            vals = {'leave_id': leave_id.id,
                 'request_date_from':leave_id.request_date_from.strftime('%Y-%m-%d') if leave_id.request_date_from else False,
                 'request_date_to': leave_id.request_date_to.strftime('%Y-%m-%d') if leave_id.request_date_to else False,
                 'name':leave_id.name, 'request_date_from_period':[('am', 'Morning'), ('pm', 'Afternoon')],
                 'period':leave_id.request_date_from_period,
                 'request_unit_half':leave_id.request_unit_half,
                 'request_unit_hours': leave_id.request_unit_hours,
                 'request_unit_custom': leave_id.request_unit_custom,
                 'request_hour_from':hour_list,
                 'hour_from': leave_id.request_hour_from or '00:00',
                 'request_hour_to':hour_list,
                 'hour_to': leave_id.request_hour_to or '00:00',
                 'number_of_days': leave_id.number_of_days,
                 'number_of_hours_display': leave_id.sudo().number_of_hours_display,
                 'employee_id': leave_id.sudo().employee_id,
                 'department_id': leave_id.department_id,
                 'holiday_status_id': leave_id.holiday_status_id,
                 'request_unit': leave_id.sudo().holiday_status_id.request_unit,
                 'timeoff_types': timeoff_types}
            return request.env['ir.ui.view']._render_template("website_holidays.holidays_edit", vals)

    @http.route('/timeoff/request/request_unit', type='json', auth="user", website=True)
    def timeoff_request_unit(self, timeoff_type):
        timeoff_type = request.env['hr.leave.type'].sudo().browse(int(timeoff_type))
        return timeoff_type.request_unit

    @http.route(['/timeoff/edit/submit'],type='json', auth="user", website=True)
    def timeoff_edit_submit(
            self, leave_id, name, request_date_from,
            request_date_to, duration, holiday_status_id=False, unit_hour=False,
            unit_half=False, period=False, hour_from=False, hour_to=False,
            **post):
        leave_id = request.env['hr.leave'].sudo().browse(int(leave_id))
        message = ''
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        vals = {}
        if not leave_id.state in ['draft', 'confirm']:
            message = "Solo se pueden modificar ausencias sin aprovar"
        if message == '':
            if name != leave_id.name:
                vals['name'] = name
            if request_date_from != '' and request_date_from != leave_id.request_date_from.strftime('%Y-%m-%d'):
                vals['request_date_from'] = datetime.strptime(request_date_from, '%Y-%m-%d').date()
            if request_date_to != '' and request_date_to != leave_id.request_date_to.strftime('%Y-%m-%d'):
                vals['request_date_to'] = datetime.strptime(request_date_to, '%Y-%m-%d').date()
                #vals['date_to'] = datetime.strptime(request_date_to, '%Y-%m-%d')
            if holiday_status_id and int(holiday_status_id) != leave_id.holiday_status_id.id:
                holiday_status_id = request.env['hr.leave.type'].sudo().browse(int(holiday_status_id))
                vals['holiday_status_id'] = int(holiday_status_id)
                if holiday_status_id.unit_hours != leave_id.request_unit_hours:
                    unit_hour_change = True
                    vals['request_unit_hours'] = holiday_status_id.request_unit_hours
            if hour_from and hour_from != '00:00' and hour_to != '00:00':
                vals['request_hour_from'] = hour_from
                vals['request_hour_to'] = hour_to
            leave_id.write(vals)
            leave_id._onchange_request_parameters()
            if vals.get('holiday_status_id'):
                leave_id.sudo()._onchange_holiday_status_id()
            message = "Cambios realizados con exito."
        return request.env['ir.ui.view']._render_template("website_holidays.holidays_request_submit", {'message':message, 'error': {}})

    @http.route('/employee/holidays/upload', type='json', auth="user", website=True)
    def upload_leave(self, leave_id):
        return request.env['ir.ui.view']._render_template("website_holidays.holidays_upload", {'leave_id':leave_id})

    @http.route(['/employee/holidays/sendattch'], type="http", auth="public", website=True)
    def website_holiday_send_attach(self, **post):
        attachment = post.get('req_attach')
        if attachment:
            data_image = base64.b64encode(attachment.read())
            leave = request.env['hr.leave'].browse(post.get('leave_id'))
            request.env['hr.leave.document'].sudo().create(
                {'name': attachment.filename,
                 'leave_id': leave.id,
                 'document_id': data_image})
        return request.redirect('/employee/leaves')

    @http.route(['/employee/holidays/downattch'], type='http', auth="public", website=True)
    def download_attachment(self, attachment_id):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        attachment = request.env['hr.leave.document'].search([('id', '=', int(attachment_id))])
        if not attachment:
            return request.redirect('/employee')
        data = io.BytesIO(base64.standard_b64decode(attachment.document_id))
        return http.send_file(data, filename=attachment.name, as_attachment=True)
    