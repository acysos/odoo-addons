# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from odoo.http import request
from odoo import http, fields


class WebsiteResumen(http.Controller):

    @http.route(
        ['/my/resumen'], type='http', auth="user", website=True)
    def portal_reumen_month(self, year=None, month=None, **kw):
        if not year or not month:
            today = fields.date.today()
            year = today.year
            month = today.month
            day = today.day
        else:
            day = 1
            year = int(year)
            month = int(month)
        date_init = date(int(year), int(month), 1)
        if month != 12:
            date_end = date(int(year), int(month)+1, 1)
        else:
            date_end = date(int(year) + 1, 1, 1)
        if month < 12:
            next_url = '/my/resumen?year=' + str(year) + \
                '&month=' + str(month + 1)
        else:
            next_url = '/my/resumen?year=' + str(year + 1) + \
                '&month=1'
        if month == 1:
            ant_url = '/my/resumen?year=' + str(year - 1) + \
                '&month=12'
        else:
            ant_url = '/my/resumen?year=' + str(year) + \
                '&month=' + str(month-1)
        if date_end > fields.date.today():
            date_end = fields.date.today()
            next_url = False
        date_limit = date(2021, 12, 20)
        if date_init < date_limit:
            date_init = date_limit
        resumen_ids = request.env['hr.day.resumen'].sudo().search([
            ('employee_id', '=', request.env.user.employee_id.id),
            ('day', '>=', date_init), ('day', '<', date_end)])
        over_qty = request.env.user.employee_id.overtime_qty
        hours = int(over_qty)
        minutes = int((over_qty*60) % 60)
        seconds = int((over_qty*3600) % 60)
        if minutes < 10:
            minutes = "0" + str(minutes)
        if seconds < 10:
            seconds = "0" + str(seconds)
        over_time = str(hours) + ":" + str(minutes) + ":" + str(seconds)
        result = {'ant_url': ant_url, 'next_url': next_url, 'resumen_ids': resumen_ids,
                  'overtime_qty': over_time}
        return request.render("website_hr_day_resumen.portal_resumen_month", result)