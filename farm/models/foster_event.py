# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


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

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise Warning(
                _("Only females can foster a group"))
        if not self.is_ready():
            raise Warning(
                _("Only lactating females can foster a group"))
        far_event = self.animal.current_cycle.farrowing_event
        self.farrowing_group = \
            far_event.event.produced_group.animal_group
        self.female_cycle = self.animal.current_cycle
        self.pair_event = self.pair_female.current_cycle
        self.trasform_group()
        super(FosterEvent, self).confirm()

    @api.one
    def trasform_group(self):
        incoming_group = \
            self.pair_event.farrowing_event.event.produced_group.animal_group
        if incoming_group.quantity < self.quantity:
            raise Warning(
                _('quantity is biger than incoming group quantity'))
        trans_eve_obj = self.env['farm.transformation.event']
        new_trans_ev = trans_eve_obj.create({
            'animal_type': 'group',
            'specie': self.specie.id,
            'farm': self.farm.id,
            'animal_group': incoming_group.id,
            'timestamp': self.timestamp,
            'from_location': incoming_group.location.id,
            'to_animal_type': 'group',
            'to_location': self.animal.location.id,
            'quantity': self.quantity,
            'to_animal_group': self.farrowing_group.id,
            })
        new_trans_ev.confirm()
        self.move = new_trans_ev.move
        foster_event_obj = self.env['farm.foster.event']
        foster_event_obj.create({
            'aniaml': self.pair_female.id,
            'farm': self.farm.id,
            'state': 'validated',
            'animal_type': 'female',
            'farrowing_group': incoming_group.id,
            'quantity': self.quantity,
            'pair_female': self.animal.id,
            'pair_event': self.female_cycle.id,
            'female_cycle': self.pair_event.id,
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
