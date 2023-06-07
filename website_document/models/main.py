# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request
import base64
import io
import os

class WebsiteDocument(http.Controller):

    def get_domain(self, user_id):
        return ['|',('all_users', '=', True), ('autoriced_users', 'in', [request.uid])]

    def get_parent_folder(self, doc, current_folder=False):
        if doc.category_id.id != current_folder and doc.category_id.parent_id:
            folder = doc.category_id
            if folder.parent_id:
                control = True
                while control:
                    if current_folder:
                        if folder.parent_id.id == current_folder:
                            control = False
                        else:
                            folder = folder.parent_id
                    elif folder.parent_id:
                        folder = folder.parent_id
                    else:
                        control = False
            elif folder.id == current_folder:
                folder = doc.category_id
        elif current_folder:
            if doc.category_id.id == current_folder:
                folder = False
            else:
                folder = doc.category_id
        else:
            folder = folder = doc.category_id
        return folder

    def get_document_values(self, values, category, domain, root):
        control_cat = []
        if category:
            categ = request.env['document.category'].sudo().browse(int(category))
            if categ.parent_id:
                values['go_back'] = root + str(categ.parent_id.id)
            domain.append(('category_id', 'child_of', category))
            documents = request.env['document.document'].search(domain)
            values['folder'] = request.env['document.category'].browse(category).name
            for doc in documents:
                folder = self.get_parent_folder(doc, category)
                if not folder or folder.id == category:
                    values['documents'].append(doc)
                else:
                    if folder.id not in control_cat:
                        url = root+ str(folder.id)
                        values['categories'].append({'category':folder,
                                                     'cat_url': url})
                        control_cat.append(folder.id)
        else:
            values['go_back'] = "/employee"
            documents = request.env['document.document'].search(domain)
            for doc in documents:
                if doc.category_id:
                    folder = self.get_parent_folder(doc)
                    if folder.id not in control_cat:
                        url = root + str(folder.id)
                        values['categories'].append(
                            {'category': folder, 'cat_url': url})
                        control_cat.append(folder.id)
                else:
                    values['documents'].append(doc)
        return values

    @http.route(['/ayuda', '/ayuda/category/<int:category>'], type='http', auth="public", website=True)
    def website_document_help(self, category=None, **post):
        if not request.env.user.employee_id:
            return request.redirect('/web/login')
        domain = [('is_help', '=', True)]
        values = {'documents': [], 'categories': [], 'folder': False,
                  'help': True, 'go_back': '/ayuda'}
        values = self.get_document_values(values, category, domain, '/ayuda/category/')
        return request.render('website_document.website_document', values)

    @http.route(['/documentos', '/documentos/category/<int:category>'], type='http', auth="public", website=True)
    def website_document(self, category=None, **post):
        if not request.env.user.employee_id:
            return request.redirect('/web/login')
        domain = self.get_domain(request.uid)
        values = {'documents': [], 'categories': [], 'folder': False,
                  'help': False, 'go_back': '/documentos'}
        values = self.get_document_values(values, category, domain, '/documentos/category/')
        return request.render('website_document.website_document', values)

    @http.route(['/documentos/ver'], type='http', auth="public", website=True)
    def website_document_view(self, attachment_id):
        if not request.env.user.employee_id:
            return request.redirect('/web/login')
        attachment = request.env['document.document'].search([('id', '=', int(attachment_id))])
        if not attachment:
            return request.redirect('/employee')
        data = io.BytesIO(base64.standard_b64decode(attachment.document))
        file = os.system(attachment.document)
        return request.render('website_document.website_document_viewer', {'attach': file})

    @http.route(['/download/attachment'], type='http', auth="public", website=True)
    def download_attachment(self, attachment_id):
        if not request.env.user.employee_id:
            return request.redirect('/web/login')
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        attachment = request.env['document.document'].sudo().search([('id', '=', int(attachment_id))])
        if not attachment:
            return request.redirect('/employee')
        if not attachment.is_help:
            domain = self.get_domain(request.uid)
            documents = request.env['document.document'].sudo().search(domain)
            if attachment not in documents:
                return request.redirect('/employee')
        data = io.BytesIO(base64.standard_b64decode(attachment.document))
        attachment.sudo().create_log(request.uid, 'donwload')
        return http.send_file(data, filename=attachment.name, as_attachment=True)
