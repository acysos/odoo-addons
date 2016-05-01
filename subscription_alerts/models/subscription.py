# -*- coding: utf-8 -*-
# © 2016 Acysos S.L. - Ignacio Ibeas (http://acysos.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import models, fields, exceptions, api, _
import datetime
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class SubscriptionSubscription(models.Model):
    _inherit = 'subscription.subscription'

    email_template = fields.Many2one(comodel_name='email.template',
                                     string='Email Template')

    @api.multi
    def _send_alerts(self):
        logger.info('Send subscriptions alerts')
        days = self.env.user.company_id.subs_alert_days
        today = datetime.date.today()
        time = datetime.time(0, 0, 0)
        date_start = (datetime.datetime.combine(today, time) - \
            relativedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        time = datetime.time(23, 59, 59)
        date_end = (datetime.datetime.combine(today, time) - \
            relativedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        cron_obj = self.env['ir.cron']
        crons = cron_obj.search([('nextcall','>=',date_start),
                                 ('nextcall','<=',date_end)])
        cron_ids = []
        for cron in crons:
            cron_ids.append(cron.id)
        subscriptions = self.search([('cron_id', 'in', cron_ids)])
        for subscription in subscriptions:
            if subscription.email_template:
                print self.pool['email.template'].send_mail(
                   self.env.cr, self.env.uid, subscription.email_template.id,
                   subscription.id, force_send=True, context=self.env.context)
