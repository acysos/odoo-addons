# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class FarrowingProblem(models.Model):
    _name = 'farm.farrowing.problem'

    name = fields.Char(string='Name', required=True, traslate=True)


class FarrowingEvent(models.Model):
    _name = 'farm.farrowing.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}
    _rec_name = 'animal'
    _auto = True

    live = fields.Integer(string='Live')
    stillborn = fields.Integer(string='Stillborn')
    mummified = fields.Integer(string='Mummified')
    dead = fields.Integer(string='Dead', compute='get_dead')
    problem = fields.Many2one(comodel_name='farm.farrowing.problem',
                              string='Problem')
    female_cycle = fields.One2many(
        comodel_name='farm.farrowing.event_female_cycle',
        inverse_name='event', column1='cycle',
        string='Female Cycle')
    produced_group = fields.One2many(
        comodel_name='farm.farrowing.event_group',
        inverse_name='event', column1='animal_group', string='Produced Group')
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move')

    @api.one
    def get_dead(self):
        self.dead = (self.stillborn or 0) + (self.mummified or 0)

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise Warning(
                _("Only females can be farrow"))
        if not self.is_ready():
            raise Warning(
                _("Only diagnosticated pregnant females can be farrow"))
        if self.dead == 0 and self.live == 0:
            raise Warning(
                _('no deads and no lives'))
        farrowing_cycle_obj = self.env['farm.farrowing.event_female_cycle']
        farrrowing_animalGroup_obj = self.env['farm.farrowing.event_group']
        location_obj = self.env['farm.foster.locations']
        foster_locations = []
        for loc in self.animal.specie.foster_location:
            foster_locations.append(loc.id)
        foster_location = location_obj.search(
            [('location.location_id', '=', self.farm.id),
             ('id', 'in', foster_locations),
             ],
            ).location
        farrowing_cycle_obj.create({
            'event': self.id,
            'cycle': self.animal.cycles[-1].id})
        if self.live != 0:
            self.get_female_move(foster_location)
            new_group = self.get_produced_group()
            farrrowing_animalGroup_obj.create({
                'event': self.id,
                'animal_group': new_group[0].id
                })
        self.animal.current_cycle.update_state(self)
        for line in self.animal.account.line_ids:
            line.account_id = new_group[0].account
            line.name = 'Farrow Cost'
        super(FarrowingEvent, self).confirm()

    @api.one
    def get_female_move(self, foster_loc):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        target_quant = quants_obj.search([
            ('lot_id', '=', self.animal.lot.lot.id),
            ('location_id', '=', self.animal.location.id),
            ])
        fem_move = moves_obj.create({
            'name': 'foster-mother-' + self.animal.lot.lot.name,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': self.animal.lot.lot.product_id.id,
            'product_uom_qty': 1,
            'product_uom':
                self.animal.lot.lot.product_id.product_tmpl_id.uom_id.id,
            'location_id': self.animal.location.id,
            'location_dest_id': foster_loc.id,
            'company_id': self.animal.farm.company_id.id, })
        for q in target_quant:
            q.reservation_id = fem_move.id
        fem_move.action_done()
        self.female_move = fem_move
        self.animal.location = foster_loc
        tags_obj = self.env['farm.tags']
        tag = tags_obj.search([
                ('name', '=', self.farm.name+'-mated')])
        tag.animal = [(3, self.animal.id)]
        new_tag = tags_obj.search([
            ('name', '=', self.farm.name + '-lact')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': self.farm.name + '-lact',
                                       })
        self.animal.tags = [(6, 0, [new_tag.id, ])]

    @api.one
    def get_produced_group(self):
        animalGroup_obj = self.env['farm.animal.group']
        tags_obj = self.env['farm.tags']
        tags = []
        new_tag = tags_obj.search([
            ('name', '=', self.farm.name + '-lact')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': self.farm.name + '-lact',
                                       })
        tags.append(new_tag.id)
        new_group = animalGroup_obj.create({
            'specie': self.specie.id,
            'breed': self.animal.breed.id,
            'initial_location': self.animal.location.id,
            'initial_quantity': self.live,
            'farm': self.animal.farm.id,
            'origin': 'raised',
            'arrival_date': self.timestamp,
            'tags': [(6, 0, tags)],
            })
        new_group.state = 'lactating'
        return new_group

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.animal.current_cycle.state == 'pregnat':
            return True
        else:
            return False


class FarrowingEventFemaleCycle(models.Model):
    _name = 'farm.farrowing.event_female_cycle'

    event = fields.Many2one(comodel_name='farm.farrowing.event',
                            string='Farrowing Event', required=True,
                            ondelete='RESTRICT')
    cycle = fields.Many2one('farm.animal.female_cycle', string='Female Cycle',
                            required=True, ondelete='RESTRICT')


class FarrowingEventAnimalGroup(models.Model):
    _name = 'farm.farrowing.event_group'
    _rec_name = 'animal_group'

    event = fields.Many2one(comodel_name='farm.farrowing.event',
                            string='Farrowing Event', required=True,
                            ondelete='RESTRICT')
    animal_group = fields.Many2one(comodel_name='farm.animal.group',
                                   string='Group', required=True,
                                   ondelete='RESTRICT')

    @api.multi
    def name_get(self):
        displayName = []
        for group in self:
            displayName.append((group.id, group.animal_group.number))
        return displayName
