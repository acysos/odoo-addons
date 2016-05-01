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

class LarpPlot(models.Model):
    _name = 'larp.plot'
    
    name = fields.Char(string='Name', required=True)
    parent_id = fields.Many2one(string='Parent Plot', comodel_name='larp.plot')
    event = fields.Many2one(string='Game', comodel_name='event.event',
                            required=True, ondelete='cascade')
    plot = fields.Html(string='Plot')
    player_ids = fields.Many2many(string='Players', comodel_name='larp.player',
                                  relation='larp_player_plot', column1='plot',
                                  column2='player')
    skills = fields.Many2many(string='Skills', comodel_name='larp.skill',
                              relation='larp_player_skill', column1='plot',
                              column2='skill',
                              help='Skills needed to do this plot')
    