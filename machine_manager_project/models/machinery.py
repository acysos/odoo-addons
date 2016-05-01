# -*- coding: utf-8 -*-
# © 2016 Acysos S.L. - Ignacio Ibeas (http://acysos.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import models, fields, exceptions, api, _


class Machinery(models.Model):
    _inherit = "machinery"
    
    partner_id = fields.Many2one(comodel_name='res.partner', string='Owner')
