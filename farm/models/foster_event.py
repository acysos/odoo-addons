# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning


class FosterEvent(models.Model):
    _name = 'farm.foster.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}
    _auto = True

    farrowing_group = fields.Many2one(comodel_name='farm.animal.group',
                                      string='Farrowing Group')
    quantity = fields.Integer(string='Fosters',
                                     help='If this quantity is negative it is'
                                     'a Foster Out.')
    pair_female = fields.Many2one(comodel_name='farm.animal',
                                  string='Pair Female', required=True,
                                  domain=[('type', '=', 'female'),
                                          ('current_cycle', '!=', None), ])
    pair_event = fields.Many2one(comodel_name='farm.animal.female_cycle',
                                 string='Female Cycle')
    female_cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                                   string='Female Cycle')
    move = fields.Many2one(comodel_name='stock.move', string='Female Cycle')


    def confirm(self):
        for res in self:
            if not res.is_compatible():
                raise Warning(
                    _("Only females can foster a group"))
            if not res.is_ready():
                raise Warning(
                    _("Only lactating females can foster a group"))
            far_event = res.animal.current_cycle.farrowing_event
            res.farrowing_group = \
                far_event.event.produced_group.animal_group
            res.female_cycle = res.animal.current_cycle
            res.pair_event = res.pair_female.current_cycle
            res.trasform_group()
        super(FosterEvent, self).confirm()

    def trasform_group(self):
        for res in self:
            incoming_group = \
                res.pair_event.farrowing_event.event.produced_group.animal_group
            if incoming_group.quantity < res.quantity:
                raise Warning(
                    _('quantity is biger than incoming group quantity'))
            trans_eve_obj = res.env['farm.transformation.event']
            new_trans_ev = trans_eve_obj.create({
                'animal_type': 'group',
                'specie': res.specie.id,
                'farm': res.farm.id,
                'animal_group': incoming_group.id,
                'timestamp': res.timestamp,
                'from_location': incoming_group.location.id,
                'to_animal_type': 'group',
                'to_location': res.animal.location.id,
                'quantity': res.quantity,
                'to_animal_group': res.farrowing_group.id,
                })
            new_trans_ev.confirm()
            res.move = new_trans_ev.move
            foster_event_obj = res.env['farm.foster.event']
            foster_event_obj.create({
                'aniaml': res.pair_female.id,
                'farm': res.farm.id,
                'state': 'validated',
                'animal_type': 'female',
                'farrowing_group': incoming_group.id,
                'quantity': res.quantity,
                'pair_female': res.animal.id,
                'pair_event': res.female_cycle.id,
                'female_cycle': res.pair_event.id,
                'move': new_trans_ev.move.id})

    def is_ready(self):
        if self.animal.current_cycle.state == 'lactating' and \
                self.pair_female.current_cycle.state == 'lactating':
            return True
        else:
            return False

    def is_compatible(self):
        if self.animal.type == 'female' and self.pair_female.type == 'female':
            return True
        else:
            return False
