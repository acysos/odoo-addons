# -*- coding: utf-8 -*-
# © 2016 Acysos S.L. - Ignacio Ibeas (http://acysos.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import models, fields, exceptions, api, _

    
class Project(models.Model):
    _inherit = "project.project"
    
    machine = fields.Many2one(comodel_name='machinery', string='Machinery')

class Task(models.Model):
    _inherit = "project.task"

    machine = fields.Many2one(comodel_name='machinery', string='Machine')
