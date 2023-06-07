# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class documentDocument(models.Model):
    _name = 'document.document'
    _inherit = ['mail.thread']

    def default_user(self):
        return self.env.user

    name = fields.Char(string='Titulo', required=True)
    document = fields.Binary(string="Documento", required=True)
    file_name = fields.Char()
    all_users = fields.Boolean(string="Visible todo el mundo")
    autoriced_users = fields.Many2many(string="Empleados permitidos",
                                       comodel_name="res.users")
    category_id = fields.Many2one(
        string="Categoria", comodel_name="document.category")
    first_mail = fields.Boolean(string="Enviado por correo")
    donwload_url = fields.Char(compute='get_donwload_url', store=True)
    user_id = fields.Many2one(
        string="responsable", comodel_name="res.users", default=default_user)
    last_reminder = fields.Date(string="Ultimo recordatorio")
    control_revised = fields.Many2many(
        string="Faltan por descargar", comodel_name="res.partner")
    is_help = fields.Boolean('Ayuda')

    def send_custom_mail(self):
        context = self.env.context.copy()
        context['active_ids'] = self.ids
        return {
            'name': ('Document send mail'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'document.send.wiz',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            }

    def get_revised(self):
        for res in self:
            partners = []
            do_partner = []
            do_users = []
            logins = self.env['document.log'].search(
                [('document_id','=', res.id)])
            for log in logins:
                if log.user_id not in do_users:
                    do_users.append(log.user_id)
            for user in do_users:
                do_partner.append(user.partner_id.id)
            if res.all_users:
                employees = self.env['hr.employee'].search(
                    [('active', '=', True), ('department_id', '!=', False)])
                for employee in employees:
                    if employee.user_id.partner_id.id not in do_partner:
                        partners.append(employee.user_id.partner_id.id)
            else:
                for unser in res.autoriced_users:
                    if unser.partner_id.id not in do_partner:
                        partners.append(unser.partner_id.id)
            res.control_revised = [(6, 0, partners)]

    @api.depends('category_id')
    def get_donwload_url(self):
        for res in self:
            if res.category_id:
                res.donwload_url = '/documentos/category/' + str(res.category_id.id)
            else:
                res.donwload_url = "/documentos"

    def send_first_mail(self):
        partners = []
        dest_patners = ''
        if self.all_users:
            employees = self.env['hr.employee'].search(
                [('active', '=', True), ('department_id', '!=', False)])
            for employee in employees:
                partners.append(employee.user_id.partner_id.id)
                if employee.user_id.partner_id:
                    dest_patners += str(employee.user_id.partner_id.id) + ','
        else:
            for unser in self.autoriced_users:
                partners.append(unser.partner_id.id)
                dest_patners += str(unser.partner_id.id) + ',' 
        self.message_subscribe(partner_ids=partners)
        template = self.env.ref(
            'website_document.email_template_new_document', False)
        template.write({'partner_to': dest_patners})
        template.send_mail(self.id, True)
        self.first_mail = True
        self.get_revised()

    def send_reminder_mail(self):
        partners = []
        dest_patners = ''
        for partner in self.control_revised:
            partners.append(partner.id)
            dest_patners += str(partner.id) + ',' 
        self.message_subscribe(partner_ids=partners)
        template = self.env.ref(
            'website_document.email_template_document_remenber', False)
        template.write({'partner_to': dest_patners})
        template.send_mail(self.id, True)
        self.last_reminder = fields.Date.today()

    def create_log(self, user_id, event):
        doc_log = self.sudo().env['document.log']
        control = True
        if event == 'first_visit':
            old_log = doc_log.sudo().search([('document_id','=', self.id),
                                   ('user_id', '=', user_id)])
            if old_log:
                control = False
        if control:
            doc_log.sudo().create(
                {'document_id': self.id,
                 'user_id': user_id,
                 'event_type': event,
                 'event_date': fields.Datetime.now()})
            partner_id = self.env['res.users'].browse(user_id).partner_id
            if partner_id in self.control_revised:
                self.control_revised = [(3, partner_id.id)]

    def open_log(self):
        log_ids = self.env['document.log'].search(
            [('document_id', '=', self.id)])
        action = self.env.ref(
                'website_document.website_document_log_action').read()[0]
        current_domain = "[('id', 'in', " + str(log_ids.ids) + ")]"
        action['domain'] = current_domain
        return action


class DocumentCategory(models.Model):
    _name = 'document.category'

    name = fields.Char(string="Nombre")
    document_ids = fields.One2many(
        string="Documentos", comodel_name="document.document",
        inverse_name='category_id')
    parent_id = fields.Many2one(
        string="Carpeta padre", comodel_name="document.category")
    child_ids = fields.One2many(
        string="Subcarpetas", comodel_name="document.category",
        inverse_name="parent_id")
    complete_name = fields.Char(
        'Nombre completo', compute='_compute_complete_name',
        store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class DocumentLog(models.Model):
    _name = 'document.log'

    document_id = fields.Many2one(
        comodel_name="document.document", string="Documento")
    user_id = fields.Many2one(
        comodel_name="res.users", string="empleado")
    event_date = fields.Datetime(string="Fecha")
    event_type = fields.Selection(
        [('first_visit', 'Visitado'),
         ('open', 'Habierto'),
         ('donwload', 'Descargado')], string="Evento")
