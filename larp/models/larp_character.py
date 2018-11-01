# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LarpCharacter(models.Model):
    _name = 'larp.character'

    @api.multi
    def _get_point_used(self):
        for character in self:
            character.point_used = sum(
                skill.point_experience for skill in character.skills)

    @api.onchange('skills')
    def _check_px(self):
        if self.point_used > self.point_experience:
            raise ValidationError(
                _("You can't add more skill without increase "
                  "the points of experience."))

    name = fields.Char(string='Name', required=True)
    event = fields.Many2one(
        string='LARP', comodel_name='event.event', required=True,
        ondelete='cascade')
    partner_id = fields.Many2one(
        string='Interpreter', comodel_name='res.partner')
    point_experience = fields.Integer(string='Points of experience')
    point_used = fields.Integer(
        string='Points used', compute='_get_point_used')
    skills = fields.Many2many(
        string='Skills', comodel_name='larp.skill',
        relation='larp_character_skill_rel',
        column1='larp_character_id', column2='larp_skill_id')
    plot = fields.Html(string='Principal Plot')
    plot_ids = fields.Many2many(
        string='Plots', comodel_name='larp.plot',
        relation='larp_character_plot_rel',
        column1='larp_character_id', column2='larp_plot_id')
    ticket_id = fields.Many2one(
        comodel_name='event.event.ticket', string='Ticket')
    resgistration_id = fields.Many2one(
        comodel_name='event.registration', string='Registration')

    
class LarpSkill(models.Model):
    _name = 'larp.skill'
    
    name = fields.Char(string='Name', required=True)
    event = fields.Many2one(string='LARP', comodel_name='event.event',
                            required=True, ondelete='cascade')
    point_experience = fields.Integer(string='Point of experience')
    description = fields.Html(string='Description')
    skills_depends = fields.Many2many(
        string='Skill depends', comodel_name='larp.skill',
        relation='larp_skill_depends', column1='skill', column2='skill_dep',
        help='Need these skills to get this')
