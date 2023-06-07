# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import request
from odoo import http, fields
from datetime import date, datetime, timedelta
import calendar
import pytz

DATEFORMAT = '%Y-%m-%d %H:%M:%S'

Meses = {1: 'Enero', 2: 'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6: 'Junio',
         7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre',
         11: 'Noviembre', 12: 'Diciembre'}

class WebsiteWorkCalendar(http.Controller):

    def get_week_values(self, week, month, year, resumen_obj, employee):
        underflow = date(year, month, 1)
        if month != 12:
            overflow = date(year, month +1, 1)
        else:
            overflow = date(year +1, 1, 1)
        aux_week = []
        exceps = {}
        public_holidays = request.env['hr.holidays.public'].sudo().search([
            ('year', '=', year)])
        public_holidays_days = []
        for holi in public_holidays.line_ids:
            if not holi.state_ids or employee.address_id.state_id.id in holi.state_ids.ids:
                public_holidays_days.append(holi.date)
        for day in week:
            day_dict = {'number': 0, 'fest': False, 'aus': False,
                        'back_c': 'text-align:right;padding:5px', 'num_c':False, 'date': day,}
            if day < overflow and day >= underflow:
                day_dict['number'] = day.day
                resumen = resumen_obj.sudo().search([
                    ('employee_id', '=', employee.id), ('day', '=', day)])
                if resumen:
                    if resumen.resume_line and not resumen.leave_ids:
                        exct = resumen.calendar_id.search_exception(resumen)
                        if exct:
                            day_dict['back_c'] = 'background-color:' + \
                            exct.background_color + ';text-align:right;padding:5px'
                            day_dict['num_c'] = 'color:' + exct.number_color
                            if exct.name not in exceps.keys():
                                exceps[exct.name] = {
                                    'back_c': 'background-color:' + exct.background_color,
                                    'num_c':'color:' + exct.number_color}
                        else:
                            if resumen.calendar_id:
                                day_dict['back_c'] = 'background-color:' + \
                                    resumen.calendar_id.background_color + \
                                    ';text-align:right;padding:5px'
                                day_dict['num_c'] = 'color:' + resumen.calendar_id.number_color
                    else:
                        if resumen.leave_ids:
                            if resumen.leave_ids[0].holiday_status_id.include_in_theoretical:
                                day_dict['aus'] = 'no_j'
                            elif resumen.leave_ids[0].holiday_status_id.is_holyday:
                                day_dict['aus'] = 'holy'
                            else:
                                day_dict['aus'] = 'si_j'
                elif day.weekday() >= 5 or day in public_holidays_days:
                    day_dict['fest'] = True
                else:
                    day_dict['turno'] = 'other'
            aux_week.append(day_dict)
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        print(aux_week)
        return [aux_week, exceps]

    def get_exceptions(self, color_e, aux_week):
        for k, c_exp in aux_week.items():
            if k not in color_e.keys():
                color_e[k] = c_exp
        return color_e

    @http.route(['/calendario'], type='http', auth='public', website=True)
    def website_calendary_fold(self, month=None, **kw):
        resumen_obj = request.env['hr.day.resumen']
        employee = request.env.user.employee_id
        today = fields.date.today()
        if not month:
            month = today.month
        else:
            month = int(month)
        year = today.year
        cal = calendar.Calendar()
        mes = {'name': Meses[month], 'weeks': [], 'url': False}
        color_excp = {}
        for week in cal.monthdatescalendar(year, month):
            aux_week = self.get_week_values(
                week, month, year, resumen_obj, employee)
            mes['weeks'].append(aux_week[0])
            color_excp = self.get_exceptions(color_excp, aux_week[1])
        if month == 1:
            ant = False
        else:
            ant = '/calendario?month=' + str(month - 1)
        if month == 12:
            next = False
        else:
            next = '/calendario?month=' + str(month + 1)
        result = {'month': mes, 'year_str': str(year), 'ant_url': ant,
                 'next_url': next, 'color_excep': color_excp}
        return request.render('website_work_calendary.website_calendary_month', result)

    @http.route(['/calendario/dia'], type='json', auth='public', website=True)
    def website_calendar_schedule(self, day, **kw):
        resumen_obj = request.env['hr.day.resumen']
        employee = request.env.user.employee_id
        resumen = resumen_obj.sudo().search([
                    ('employee_id', '=', employee.id), ('day', '=', day)])
        schedules = []
        for r_line in resumen.resume_line:
            user_tz = request.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            aux_begin = pytz.utc.localize(r_line.begin).astimezone(local)
            aux_end = pytz.utc.localize(r_line.end).astimezone(local)
            begin = "{:d}:{:02d}".format(aux_begin.hour, aux_begin.minute)
            end = "{:d}:{:02d}".format(aux_end.hour, aux_end.minute)
            schedules.append({'init': begin, 'fin': end})
        vals = {'day': day, 'schedules': schedules}
        return request.env['ir.ui.view']._render_template(
            'website_work_calendary.website_calendary_schedule', vals)

    @http.route(['/calendario/año'], type='http', auth='public', website=True)
    def website_calendar(self):
        today = fields.date.today()
        year = today.year
        cal = calendar.Calendar()
        resumen_obj = request.env['hr.day.resumen']
        employee = request.env.user.employee_id
        months = [{'name':'Enero', 'weeks':[]}, {'name':'Febrero', 'weeks':[]},
                 {'name':'Marzo', 'weeks':[]}, {'name':'Abril', 'weeks':[]},
                 {'name':'Mayo', 'weeks':[]}, {'name':'Junio', 'weeks':[]},
                 {'name':'Julio', 'weeks':[]}, {'name':'Agosto', 'weeks':[]},
                 {'name':'Septiembre', 'weeks':[]}, {'name':'Octubre', 'weeks':[]},
                 {'name':'Noviembre', 'weeks':[]}, {'name':'Diciembre', 'weeks':[]}]
        month = 1
        color_e = {}
        for mes in months:
            for week in cal.monthdatescalendar(year, month):
                aux_week = self.get_week_values(
                    week, month, year, resumen_obj, employee)
                mes['weeks'].append(aux_week[0])
                mes['url'] = '/calendario?month=' + str(month)
                color_e = self.get_exceptions(color_e, aux_week[1])
            month += 1
        return request.render('website_work_calendary.website_calendary_main',
                              {'months':months, 'color_excep': color_e})
