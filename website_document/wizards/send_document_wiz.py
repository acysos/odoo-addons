# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2021  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class DocumentSendWiz(models.TransientModel):
    _name = 'document.send.wiz'

    def _default_document(self):
        return self.env['document.document'].browse(
            self._context.get('active_ids'))

    document_id = fields.Many2one(
        string='Documento', comodel_name='document.document',
        default=_default_document)
    user_ids = fields.Many2many(
        string="Empleados", comodel_name="res.users")


    def action_done(self):
        dest_patners = ''
        for user in self.user_ids:
            dest_patners += str(user.partner_id.id) + ','
            self.document_id.control_revised = [(4, user.partner_id.id)]
        template = self.env.ref(
            'website_document.email_template_new_document', False)
        template.write({'partner_to': dest_patners})
        template.send_mail(self.document_id.id, True)
