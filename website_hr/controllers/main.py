# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2020  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import HTTPException
from odoo.addons.portal.controllers.portal import CustomerPortal


class WebsiteHr(http.Controller):

    @http.route('/employee', type='http', auth="public", website=True)
    def hr_menu(self, page=0, **post):
        if not request.env.user.employee_id:
            return request.redirect('/web/login')
        values = {'ext_attendance': request.env.user.employee_id.ext_attendance}
        response = request.render("website_hr.website_hr_menu", values)
        return response

class CustomerPortal(CustomerPortal):
    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        return request.redirect('/employee')

#     @http.route('/employee/attendance', type='http', auth="public", website=True)
#     def hr_attendance(self, page=0, **post):
#         user = request.env.user
#         employee = request.env['hr.employee'].search(
#             [('user_id', '=', user.id)])
#         if not employee:
#             return HTTPException(description=_(
#                 'Only employees can access this site'))
#         values = {}
#         response = request.render('website_hr.website_hr_attendance', values)
#         return response
