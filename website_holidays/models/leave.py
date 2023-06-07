# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import HOURS_PER_DAY, float_to_time
from odoo.tools.float_utils import float_round

DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    available_portal = fields.Boolean(
        string="Petición por el portal", default=True)

    def name_get_portal(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        name = self.with_context(lang=employee.user_id.lang).name
        if self.allocation_type != 'no':
            name = "%(name)s (%(count)s)" % {
                'name': name,
                'count': _('%g remaining out of %g') % (
                    float_round(self.virtual_remaining_leaves, precision_digits=2) or 0.0,
                    float_round(self.max_leaves, precision_digits=2) or 0.0,
                ) + (_(' hours') if self.request_unit == 'hour' else _(' days'))
            }
        return name

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    documents_ids = fields.One2many(
        string="Justificantes", comodel_name="hr.leave.document",
        inverse_name='leave_id')

    @api.model
    def get_rpc_days(self, date_from, date_to, employee_id):
        print('+++++++++++++++++++++++++++++++++++++++++++')
        print(employee_id)
        date_from = datetime.strptime((date_from + ' 03:00:00'), '%Y-%m-%d %H:%M:%S')
        date_to = datetime.strptime(date_to +' 21:00:00', '%Y-%m-%d %H:%M:%S')
        return self.sudo()._get_number_of_days(
            date_from, date_to, int(employee_id))['days']

    def send_leave_mail(self, leave):
        if leave.holiday_status_id.is_holyday:
            template = self.env.ref(
                'website_holidays.email_template_holiday_change', False)
        else:
            template = self.env.ref(
                'website_holidays.email_template_leave_change', False)
        template.send_mail(leave.id, True)

    def action_refuse(self):
        result = super(HrLeave, self).action_refuse()
        for res in self:
            res.send_leave_mail(res)
        return result

    def action_validate(self):
        result = super(HrLeave, self).action_validate()
        for res in self:
            res.send_leave_mail(res)
        return result

    def action_approve(self):
        result = super(HrLeave, self).action_approve()
        for res in self:
            res.send_leave_mail(res)
        return result

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'employee_id', 'request_date_to')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        resource_calendar_id = self.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
        domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
        attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)

        # Must be sorted by dayofweek ASC and day_period DESC
        attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))

        default_value = DummyAttendance(0, 0, 0, 'morning', False)

        if resource_calendar_id.two_weeks_calendar:
            # find week type of start_date
            start_week_type = int(math.floor((self.request_date_from.toordinal() - 1) / 7) % 2)
            attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == start_week_type]
            attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != start_week_type]
            # First, add days of actual week coming after date_from
            attendance_filtred = [att for att in attendance_actual_week if int(att.dayofweek) >= self.request_date_from.weekday()]
            # Second, add days of the other type of week
            attendance_filtred += list(attendance_actual_next_week)
            # Third, add days of actual week (to consider days that we have remove first because they coming before date_from)
            attendance_filtred += list(attendance_actual_week)

            end_week_type = int(math.floor((self.request_date_to.toordinal() - 1) / 7) % 2)
            attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == end_week_type]
            attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != end_week_type]
            attendance_filtred_reversed = list(reversed([att for att in attendance_actual_week if int(att.dayofweek) <= self.request_date_to.weekday()]))
            attendance_filtred_reversed += list(reversed(attendance_actual_next_week))
            attendance_filtred_reversed += list(reversed(attendance_actual_week))

            # find first attendance coming after first_day
            attendance_from = attendance_filtred[0]
            # find last attendance coming before last_day
            attendance_to = attendance_filtred_reversed[0]
        else:
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()), attendances[0] if attendances else default_value)
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()), attendances[-1] if attendances else default_value)
        compensated_request_date_from = self.request_date_from
        compensated_request_date_to = self.request_date_to

        if self.request_unit_half:
            if self.request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
        elif self.request_unit_hours:
            hour_from = float_to_time(float(self.request_hour_from))
            hour_to = float_to_time(float(self.request_hour_to))
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
            compensated_request_date_from = self._adjust_date_based_on_tz(self.request_date_from, hour_from)    
            compensated_request_date_to = self._adjust_date_based_on_tz(self.request_date_to, hour_to)  
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)
        date_from = timezone(self.tz).localize(datetime.combine(compensated_request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
        date_to = timezone(self.tz).localize(datetime.combine(compensated_request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)
        self.write({'date_from': date_from, 'date_to': date_to})


class HrLeaveDocument(models.Model):
    _name = 'hr.leave.document'

    name = fields.Char(string='Titulo', required=True)
    leave_id = fields.Many2one(string="Ausencia", comodel_name='hr.leave')
    document_id = fields.Binary(string="Documento", required=True)
