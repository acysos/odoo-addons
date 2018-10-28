# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _


class event_type(models.Model):
    _inherit = 'event.type'
    
    larp_game = fields.Boolean(string='LARP')
    
    
class EventEvent(models.Model):
    _inherit = 'event.event'
    
    larp_game = fields.Boolean(
        string='LARP Game', related='event_type_id.larp_game')
    larp_menu = fields.Many2one(string='Menu', comodel_name='ir.ui.menu')
    larp_menu_ids = fields.Char(string='Menu IDS')
    
    @api.model
    def _get_menu_parent_id(self, module, id_menu):
        _, menu_id = self.env['ir.model.data'].get_object_reference(
            module, id_menu)
        return menu_id
    
    @api.one
    def button_confirm(self):
        super(EventEvent, self).button_confirm()
        if self.event_type_id and self.event_type_id.larp_game and \
                not self.larp_menu:
            menu_ids = []
            menu_obj = self.env['ir.ui.menu']
            action_obj = self.env['ir.actions.act_window']
            # LARP parent Menu
            gmenu = menu_obj.sudo().create({
                'name': self.name,
                'parent_id': self._get_menu_parent_id('larp', 'menu_larp_game')
            })
            menu_ids.append(gmenu.id)
            
            self.larp_menu = gmenu.id
            
            # LARP configuration Menu
            cmenu = menu_obj.sudo().create({
                'name':_('Configuration'),
                'parent_id': gmenu.id,
                'sequence': 15
            })
            menu_ids.append(cmenu.id)

            # LARP Players Menu
            player_action_id = action_obj.sudo().create({
                'name': _('Players'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.player',
                'usage': 'menu',
                'domain': [('event', '=', self.id)]
            })
            player_menu = menu_obj.sudo().create({
                'name':_('Players'),
                'parent_id': gmenu.id,
                'sequence': 5,
                'action': 'ir.actions.act_window,%s' % (player_action_id.id,)
            })
            menu_ids.append(player_menu.id)

            # LARP Plots Menu
            plot_action_id = action_obj.sudo().create({
                'name': _('Plots'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.plot',
                'usage': 'menu',
                'domain': [('event', '=', self.id)]
            })
            plot_menu = menu_obj.sudo().create({
                'name':_('Plots'),
                'parent_id': gmenu.id,
                'sequence': 10,
                'action': 'ir.actions.act_window,%s' % (plot_action_id.id,)
            })
            menu_ids.append(plot_menu.id)
            
            # LARP Skills Menu
            skill_action_id = action_obj.sudo().create({
                'name': _('Skills'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.skill',
                'usage': 'menu',
                'domain': [('event', '=', self.id)]
            })
            skill_menu = menu_obj.sudo().create({
                'name':_('Skills'),
                'parent_id': cmenu.id,
                'sequence': 10,
                'action': 'ir.actions.act_window,%s' % (skill_action_id.id,)
            })
            menu_ids.append(skill_menu.id)
            self.larp_menu_ids = str(menu_ids)

    @api.one
    def button_done(self):
        super(EventEvent, self).button_done()
        if self.larp_menu:
            menus = self.env['ir.ui.menu'].browse(eval(self.larp_menu_ids))
            menus.sudo().write({'active': False})

    @api.one
    def button_draft(self):
        super(EventEvent, self).button_draft()
        if self.larp_menu:
            menus = self.env['ir.ui.menu'].browse(eval(self.larp_menu_ids))
            menus.sudo().write({'active': True})

    @api.multi
    def unlink(self):
        for event in self:
            if event.larp_menu:
                menus = self.env['ir.ui.menu'].browse(eval(self.larp_menu_ids))
                menus.sudo().unlink()
        return super(EventEvent, self).unlink()
            
            
