# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime, time
from dateutil import parser
from pytz import timezone, UTC

from odoo import fields, http, _, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.tools import format_duration, format_datetime
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        #employee_ids = request.env["hr.employee"].sudo().search([("user_id","=",request.env.uid)]).ids
        employee_id = request.env.user.employee_id
        values["attendance_count"] = request.env["hr.attendance"].sudo().search_count([("employee_id","=",employee_id.id)])
        values["format_datetime"] = format_datetime
        return values

    def _attendance_get_page_view_values(self, attendance, access_token, **kwargs):
        values = {
            "attendance": attendance,
            "format_duration": format_duration,
            "format_datetime": format_datetime,
        }
        return self._get_page_view_values(attendance, access_token, values, "my_attendances_history", True, **kwargs)

    @http.route(["/my/attendance/", "/my/attendance/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in="check_in", **kw):
        values = self._prepare_portal_layout_values()
        attendance_obj = request.env["hr.attendance"]
        employee_ids = request.env["hr.employee"].sudo().search([("user_id","=",request.env.uid)]).ids
        domain = [("employee_id","in",employee_ids)]

        if date_begin and date_end:
            domain += [("check_in",">",date_begin),("check_in","<=",date_end)]
        searchbar_sortings = {
            "newest": {"label": _("Newest"), "order": "check_in desc"},
            "oldest": {"label": _("Oldest"), "order": "check_in asc"},
        }
        if not sortby:
            sortby = "newest"
        order = searchbar_sortings[sortby]["order"]

        attendance_searchbar_inputs = {
            "check_in": {"input": "check_in", "label": _("Search in Check In")},
        }
        if search and search_in:
            search_domain = []
            if search_in == "check_in":
                check_in = parser.parse(search)
                tz = request.env.user.sudo().tz or "UTC"
                check_in_start = timezone(tz).localize(datetime.combine(check_in, time.min)).astimezone(UTC).replace(tzinfo=None)
                check_in_end = timezone(tz).localize(datetime.combine(check_in, time.max)).astimezone(UTC).replace(tzinfo=None)
                search_domain = OR([search_domain, [("check_in",">=",check_in_start),("check_in","<=",check_in_end)]])
            domain += search_domain

        attendance_count = attendance_obj.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/attendance",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        attendances = attendance_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])
        request.session["my_attendances_history"] = attendances.ids[:100]

        values.update({
            "date": date_begin,
            "date_end": date_end,
            "attendances": attendances,
            "page_name": "attendance",
            "default_url": "/my/attendance",
            "pager": pager,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "attendance_searchbar_inputs": attendance_searchbar_inputs,
            "search_in": search_in,
            "search": search,
            "format_datetime": format_datetime,
        })
        return request.render("hr_attendance_portal.portal_my_attendances", values)
    
    @http.route(["/my/attendance/<int:attendance_id>"], type="http", auth="user", website="True")
    def portal_my_attendance(self, attendance_id=None, access_token=None, **kw):
        attendance = request.env["hr.attendance"].browse(attendance_id)
        values = self._attendance_get_page_view_values(attendance, access_token, **kw)
        return request.render("hr_attendance_portal.portal_my_attendance", values)