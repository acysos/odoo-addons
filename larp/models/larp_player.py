# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api

class LarpPlayer(models.Model):
    _name = 'larp.player'
    
    name = fields.Char(string='Name', required=True)
    event = fields.Many2one(string='Game', comodel_name='event.event',
                            required=True, ondelete='cascade')
    player = fields.Many2one(string='Player', comodel_name='res.partner')
    point_experience = fields.Integer(string='Points of experience')
    skills = fields.Many2many(string='Skills', comodel_name='larp.skill',
                              relation='larp_player_skill_rel',
                              column1='larp_player_id',
                              column2='larp_skill_id')
    plot = fields.Html(string='Principal Plot')
    plot_ids = fields.Many2many(string='Plots', comodel_name='larp.plot',
                                relation='larp_player_plot_rel',
                                column1='larp_player_id',
                                column2='larp_plot_id')
    
class LarpSkill(models.Model):
    _name = 'larp.skill'
    
    name = fields.Char(string='Name', required=True)
    event = fields.Many2one(string='Game', comodel_name='event.event',
                            required=True, ondelete='cascade')
    point_experience = fields.Integer(string='Point of experience')
    description = fields.Html(string='Description')
    skills_depends = fields.Many2many(
        string='Skill depends', comodel_name='larp.skill',
        relation='larp_skill_depends', column1='skill', column2='skill_dep',
        help='Need these skills to get this')
