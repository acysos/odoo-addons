# -*- coding: utf-8 -*-

from odoo import fields, http, _, SUPERUSER_ID
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    @http.route(["/my/attendance/check_in_out"], type="http", auth="user", website="True")
    def portal_my_attendance_check_in_out(self, access_token=None, **kw):
        request.env.user.employee_id.sudo()._attendance_action_change()
        return request.redirect("/my/attendance/")