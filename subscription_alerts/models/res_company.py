# -*- coding: utf-8 -*-
# © 2016 Acysos S.L. - Ignacio Ibeas (http://acysos.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html))
from openerp import models, fields, exceptions, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    subs_alert_days = fields.Integer(
        string='Subscription Alert Days',
        help = 'Number the days before the subscruption is launched')
        