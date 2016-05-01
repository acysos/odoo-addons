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
from openerp.tools.translate import _

class event_type(models.Model):
    _inherit = 'event.type'
    
    larp_game = fields.Boolean(string='LARP Game')
    
    
class EventEvent(models.Model):
    _inherit = 'event.event'
    
    larp_game = fields.Boolean(string='LARP Game', related='type.larp_game')
    larp_menu = fields.Many2one(string='Menu', comodel_name='ir.ui.menu')
    
    @api.model
    def _get_menu_parent_id(self, module, id_menu):
        _, menu_id = self.env['ir.model.data'].get_object_reference(module,
                                                                    id_menu)
        return menu_id
    
    @api.one
    def confirm_event(self):
        super(EventEvent, self).confirm_event()
        event_vals = {}
        if self.type and self.type.larp_game:
            menu_obj = self.env['ir.ui.menu']
            action_obj = self.env['ir.actions.act_window']

            # Game parent Menu
            gmenu = menu_obj.create({'name': self.name,
                                     'parent_id': self._get_menu_parent_id(
                                         'larp', 'menu_larp_game')})
            
            self.larp_menu = gmenu.id
            
            
            # Game configuration Menu
            cmenu = menu_obj.create({'name':_('Configuration'),
                                     'parent_id': gmenu.id,
                                     'sequence': 15})

            # Game Players Menu
            player_action_id = action_obj.create({
                'name': _('Players'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.player',
                'usage': 'menu',
                'domain': [('event','=',self.id)]})
            player_menu = menu_obj.create({
                'name':_('Players'),
                'parent_id': gmenu.id,
                'sequence': 5,
                'action': 'ir.actions.act_window,%s' % (player_action_id.id,)})

            # Game Plots Menu
            plot_action_id = action_obj.create({
                'name': _('Plots'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.plot',
                'usage': 'menu',
                'domain': [('event','=',self.id)]})
            plot_menu = menu_obj.create({
                'name':_('Plots'),
                'parent_id': gmenu.id,
                'sequence': 10,
                'action': 'ir.actions.act_window,%s' % (plot_action_id.id,)})
            
            # Game Skills Menu
            skill_action_id = action_obj.create({
                'name': _('Skills'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.skill',
                'usage': 'menu',
                'domain': [('event','=',self.id)]})
            skill_menu = menu_obj.create({
                'name':_('Skills'),
                'parent_id': cmenu.id,
                'sequence': 10,
                'action': 'ir.actions.act_window,%s' % (skill_action_id.id,)})

    @api.model
    def delete_menu(self, menus):
        for menu in menus:
            if menu.child_id:
                for child in menu.child_id:
                    self.delete_menu(child)
            else:
                menu.unlink()

    @api.one
    def unlink(self):
        if self.larp_menu:
            self.delete_menu(self.larp_menu)
        super(EventEvent, self).unlink()
            
            
