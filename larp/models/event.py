# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _


class EventType(models.Model):
    _inherit = 'event.type'
    
    larp_game = fields.Boolean(string='LARP')


class EventTicket(models.Model):
    _inherit = 'event.event.ticket'

    generate_character = fields.Boolean(string="Gen. Char")
    character_generated = fields.Boolean(string="Char. Gen.")


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    larp_character = fields.Many2one(
        comodel_name='larp.character', string='LARP Character')

    @api.one
    def confirm_registration(self):
        super(EventRegistration, self).confirm_registration()
        larp_char = self.env['larp.character'].search(
            [('ticket_id', '=', self.event_ticket_id.id),
             ('partner_id', '=', False)], limit = 1)
        if larp_char:
            larp_char.partner_id = self.partner_id.id
            larp_char.registration_id = self.id
            self.larp_character = larp_char.id

    @api.one
    def button_reg_cancel(self):
        super(EventRegistration, self).button_reg_cancel()
        if self.larp_character:
            self.larp_character.partner_id = False
            self.larp_character.registration_id = False
            self.larp_character = False
        


class EventEvent(models.Model):
    _inherit = 'event.event'
    
    larp_game = fields.Boolean(
        string='LARP Game', related='event_type_id.larp_game')
    larp_menu = fields.Many2one(string='Menu', comodel_name='ir.ui.menu')
    larp_menu_ids = fields.Char(string='Menu IDS')
    default_px = fields.Integer(string='Default PX')
    
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

            # LARP Characters Menu
            player_action_id = action_obj.sudo().create({
                'name': _('Characters'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'larp.character',
                'usage': 'menu',
                'domain': [('event', '=', self.id)],
                'context': {'default_event': self.id}
            })
            player_menu = menu_obj.sudo().create({
                'name':_('Characters'),
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
                'domain': [('event', '=', self.id)],
                'context': {'default_event': self.id}
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
                'domain': [('event', '=', self.id)],
                'context': {'default_event': self.id}
            })
            skill_menu = menu_obj.sudo().create({
                'name':_('Skills'),
                'parent_id': cmenu.id,
                'sequence': 10,
                'action': 'ir.actions.act_window,%s' % (skill_action_id.id,)
            })
            menu_ids.append(skill_menu.id)
            self.larp_menu_ids = str(menu_ids)

        # Generate characters
        for ticket in self.event_ticket_ids:
            if ticket.generate_character and not ticket.character_generated:
                print(ticket.seats_max)
                if ticket.seats_max > 0:
                    count = 1
                    while count <= ticket.seats_max:
                        name = ticket.name
                        if ticket.seats_max > 1:
                            name += ' - ' + str(count)
                        char_vals = {
                            'name': name,
                            'event': self.id,
                            'point_experience': self.default_px,
                            'ticket_id': ticket.id
                        }
                        self.env['larp.character'].create(char_vals)
                        count += 1
                    ticket.character_generated = True

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
            self.env['larp.character'].search(
                [('event', '=', event.id)]).unlink()
            self.env['larp.skill'].search(
                [('event', '=', event.id)]).unlink()
            self.env['larp.plot'].search(
                [('event', '=', event.id)]).unlink()
        return super(EventEvent, self).unlink()
            
            
