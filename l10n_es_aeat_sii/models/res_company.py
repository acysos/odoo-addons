# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# (c) 2017 Studio73 - Pablo Fuentes <pablo@studio73.es>
# (c) 2017 Studio73 - Jordi Tolsà <jordi@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    sii_enabled = fields.Boolean(string='Enable SII')
    sii_test = fields.Boolean(string='Test Enviroment')
    sii_description_method = fields.Selection(
        string='SII Description Method',
        selection=[('auto', 'Automatic'), ('fixed', 'Fixed'),
                   ('manual', 'Manual')],
        default='manual',
        help='By default the description is writed by the user. If the option'
        'is auto is generated from the invoice lines')
    sii_description = fields.Char(string="SII Description")
    sii_header_sale = fields.Char(string="SII Sale header")
    sii_header_purchase = fields.Char(string="SII Purchase header")
    chart_template_id = fields.Many2one(
        comodel_name='account.chart.template', string='Chart Template')
    sii_method = fields.Selection(
        string='Method',
        selection=[('auto', 'Automatic'), ('manual', 'Manual')],
        default='auto',
        help='By default the invoice send in validate process, with manual '
        'method, there a button to send the invoice.')
    use_connector = fields.Boolean(
        string='Use connector',
        help='Check it to use connector instead to send the invoice '
        'when it is validated')

    send_mode = fields.Selection(string="Send mode",
                                 selection=[('auto', 'On validate'),
                                            ('fixed', 'At fixed time'),
                                            ('delayed', 'With delay')],
                                 default='auto')
    sent_time = fields.Float(string="Sent time")
    delay_time = fields.Float(string="Delay time")
    sii_activity_type = fields.Many2one(
        comodel_name='mail.activity.type', string="SII Activity Type",
        help="Activity types used when SII fail")
    sii_activity_user = fields.Many2one(
        comodel_name='res.users', string="SII Activity User",
        help="Set an user to overrride the invoice user in activity when SII"
        " fails")

    def _get_sii_eta(self):
        if self.send_mode == 'fixed':
            now = datetime.now()

            hour, minute = divmod(self.sent_time, 1)
            hour = int(hour)
            minute = int(minute*60)

            if now.hour > hour or (now.hour == hour and now.minute > minute):
                now += timedelta(days=1)

            return now.replace(hour=hour, minute=minute)

        elif self.send_mode == 'delayed':
            return datetime.now() + timedelta(seconds=self.delay_time * 3600)

        else:
            return None
