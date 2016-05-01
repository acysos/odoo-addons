# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api

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
    description = fields.Html(string='Descrtiption')
    skills_depends = fields.Many2many(
        string='Skill depends', comodel_name='larp.skill',
        relation='larp_skill_depends', column1='skill', column2='skill_dep',
        help='Need these skills to get this')
