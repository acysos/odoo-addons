# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo import fields, http, _
from odoo.http import request

class WebsiteEvent(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/new'],
                type='json', auth="public", methods=['POST'], website=True)
    def registration_new(self, event, **post):
        tickets = self._process_tickets_details(post)
        if event.limit_per_registration > 0:
            quantity = 0
            for ticket in tickets:
                quantity += ticket['quantity']
            if quantity > event.limit_per_registration:
                return request.env['ir.ui.view'].render_template(
                    "website_event_sale_limit_register.registration_limit",
                    {'quantity': quantity,
                     'limit': event.limit_per_registration})
        if not tickets:
            return False
        return request.env['ir.ui.view'].render_template(
            "website_event.registration_attendee_details",
            {'tickets': tickets, 'event': event})
