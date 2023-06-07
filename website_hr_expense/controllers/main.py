# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import http, fields, _
from odoo.http import request
from datetime import datetime, timedelta
from odoo.tools import float_compare
from odoo.exceptions import MissingError
import base64
import io


class WebsiteExpense(http.Controller):

    @http.route(['/employee/expenses'], type='http', auth='user', website=True)
    def website_expenses(self):
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        if not emp_id:
            request.redirect('/web/login')
        expenses = request.env['hr.expense'].sudo().search(
            [('employee_id', '=', emp_id.id)])
        return request.env.ref('website_hr_expense.website_expenses').render(
            {'expenses': expenses})

    @http.route('/expense/request', type='json', auth="user", website=True)
    def expense_request(self):
        emp = request.env.user.sudo().employee_ids[0].id if request.env.user.sudo().employee_ids else False
        product_templates = request.env['product.template'].sudo().search([
            ('can_be_expensed', '=', True)], order="name")
        products = request.env['product.product'].sudo().search(
            [('product_tmpl_id', 'in', product_templates.ids)])
        today = fields.Date.today()
        return request.env.ref('website_hr_expense.expense_request').render(
            {'products':products,
             'req_date':today,
             })

    @http.route(['/expense/requests/submit'],type='json', auth="user", website=True)
    def expense_request_submit(self,name, request_date, price_unit, qty,
                               product, payer):
        message = ''
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        if emp_id:
            try:
                vals = {'name': name,
                        'date': request_date,
                        'product_id': int(product),
                        'employee_id': emp_id.id,
                        'unit_amount': price_unit,
                        'quantity': qty,
                        'payment_mode': payer,
                        }
                request.env['hr.expense'].sudo().create(vals)
                message = _("New expense created succesfuly")
            except Exception as e:
                message = str(e)
        else:
            message = _("Expense cannot be requested as Portal User not linked with any Employee.")
        return request.env.ref('website_hr_expense.expense_request_submit').render({'message':message, 'error': {}})

    @http.route('/expense/edit', type='json', auth="user", website=True)
    def expense_edit(self, expense_id):
        if request.env.user.sudo().employee_ids:
            expense_id = request.env['hr.expense'].browse(int(expense_id))
            emp = request.env.user.sudo().employee_ids[0].id
            product_templates = request.env['product.template'].sudo().search([
                ('can_be_expensed', '=', True)], order="name")
            products = request.env['product.product'].sudo().search(
                [('product_tmpl_id', 'in', product_templates.ids)])
            vals = {'expense_id': expense_id.id,
                 'date':expense_id.date.strftime('%Y-%m-%d') if expense_id.date else False,
                 'name':expense_id.name,
                 'product_id':expense_id.product_id,
                 'product_ids': products,
                 'unit_amount': expense_id.unit_amount,
                 'quantity': expense_id.quantity,
                 'payment_mode': expense_id.payment_mode}
            return request.env.ref('website_hr_expense.expense_edit').render(vals)

    @http.route(['/expense/edit/submit'],type='json', auth="user", website=True)
    def expense_edit_submit(
            self, expense_id, name, request_date, price_unit, qty, payer,
            product, **post):
        expense_id = request.env['hr.expense'].sudo().browse(int(expense_id))
        message = ''
        user_id = request.env['res.users'].browse(request._uid)
        emp_id = user_id.sudo().employee_ids[0] if user_id.sudo().employee_ids else False
        if not expense_id.state == 'draft':
            message = _("Only draft expenses can be modified")
        if message == '':
            vals = {'name': name,
                    'date': request_date,
                    'product_id': int(product),
                    'unit_amount': price_unit,
                    'quantity': qty,
                    'payment_mode': payer,
                        }
            expense_id.write(vals)
            message = _("Changes.aply succesfuly")
        return request.env.ref('website_hr_expense.expense_request_submit').render({'message':message, 'error': {}})

    @http.route(['/expense/send'], type='http', auth='user', website=True)
    def website_send_expense(self, **post):
        print(post)
        expense_ids = []
        for k, element in post.items():
            if 'hr.expense' in str(k):
                expense_ids.append(int(element))
        if not expense_ids:
            raise MissingError('Select anyone expense')
        expense_obj = request.env['hr.expense'].sudo().browse(expense_ids)
        sheet = expense_obj.portal_create_sheet()
        sheet.sudo().action_submit_sheet()
        return request.redirect('/employee/expenses')

    @http.route('/expenses/request/product_price', type='json', auth="user", website=True)
    def product_price_request(self, product_id):
        if product_id != '':
            product = request.env['product.product'].sudo().browse(int(product_id))
            return product.standard_price
        return 0

    @http.route(['/expense/print/<int:expense_id>'], type='http', auth="public", website=True, sitemap=False)
    def print_expense(self, expense_id=False, access_token=None, **kwargs):
        expense_id = request.env['hr.expense'].sudo().browse(expense_id)
        pdf, _ = request.env.ref('hr_expense.action_report_hr_expense_sheet').sudo().render_qweb_pdf([expense_id.sheet_id.id])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

