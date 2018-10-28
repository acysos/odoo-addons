# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api

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
    