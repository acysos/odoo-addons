# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning


class FarrowingProblem(models.Model):
    _name = 'farm.farrowing.problem'

    name = fields.Char(string='Name', required=True, traslate=True)

class FarmTagsFarrowFemales(models.Model):
    _name = 'farm.tags.farrow.females'

    tag = fields.Many2one(comodel_name='farm.tags', string='Tag', required=True)
    farrow_id = fields.Many2one(comodel_name='farm.farrowing.event', string='Farrowing Event', required=True)

class FarmTagsFarrowMales(models.Model):
    _name = 'farm.tags.farrow.males'

    tag = fields.Many2one(comodel_name='farm.tags', string='Tag', required=True)
    farrow_id = fields.Many2one(comodel_name='farm.farrowing.event', string='Farrowing Event', required=True)


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
    new_tags = fields.Many2many(comodel_name='farm.tags',
                                string='New Tags')
    female_tags = fields.One2many(
        comodel_name='farm.tags.farrow.females', inverse_name='farrow_id', ondelet='cascade')
    male_tags = fields.One2many(
        comodel_name='farm.tags.farrow.males', inverse_name='farrow_id', ondelet='cascade')


    def get_dead(self):
        for res in self:
            res.dead = (res.stillborn or 0) + (res.mummified or 0)

    def confirm(self):
        for res in self:
            if not res.is_compatible():
                raise Warning(
                    _("Only females can be farrow"))
            if res.dead == 0 and res.live == 0:
                raise Warning(
                    _('no deads and no lives'))
            farrowing_cycle_obj = self.env['farm.farrowing.event_female_cycle']
            farrrowing_animalGroup_obj = self.env['farm.farrowing.event_group']
            raise_location = self.env['stock.location'].search(
                [('usage', '=', 'production')])
            if res.animal.cycles and not res.animal.cycles[-1].farrowing_event:
                current_cycle = res.animal.cycles[-1]
            else:
                current_cycle = self.env['farm.animal.female_cycle'].create({
                    'animal': res.animal.id,
                    'state': 'mated',
                    })
            farrowing_cycle_obj.create({
                'event': res.id,
                'cycle': current_cycle.id})
            if res.live != 0:
                res.get_female_move(raise_location)
                new_group = res.get_produced_group()
                farrrowing_animalGroup_obj.create({
                    'event': res.id,
                    'animal_group': new_group[0].id
                    })
                res.animal.current_cycle.update_state(res)

        return super(FarrowingEvent, self).confirm()

    def get_female_move(self, foster_loc):
        moves_obj = self.env['stock.move']
        m_line_obj = self.env['stock.move.line']
        if foster_loc != self.animal.location:
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
                'company_id': self.animal.farm.company_id.id,
                'picked': True,})
            m_line_obj.create({
                'move_id': fem_move.id,
                'product_id': self.animal.lot.lot.product_id.id,
                'product_uom_id':
                    self.animal.lot.lot.product_id.product_tmpl_id.uom_id.id,
                'quantity': 1,
                'location_id': self.animal.location.id,
                'location_dest_id': foster_loc.id,
                'lot_id': self.animal.lot.lot.id,
                'lot_name': self.animal.lot.lot.name,
                'company_id': self.animal.farm.company_id.id,
                })
            fem_move._action_done()
            self.move = fem_move
            self.animal.location = foster_loc
        """
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
        """

    def get_produced_group(self):
        animalGroup_obj = self.env['farm.animal.group']
        tags_obj = self.env['farm.tags']
        tags = []
        female_tags = []
        male_tags = []
        if self.new_tags:
            for tag in self.new_tags:
                tags.append(tag.id)
            for ftag in self.female_tags:
                female_tags.append(ftag.tag.id)
            for mtag in self.male_tags:
                male_tags.append(mtag.tag.id)
        else:
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
        for ftag in female_tags:
            self.env['farm.tags.females'].create({
                'tag': ftag,
                'animal_group': new_group.id,
                })
        for mtag in male_tags:
            self.env['farm.tags.males'].create({
                'tag': mtag,
                'animal_group': new_group.id,
                })
        new_group.state = 'lactating'
        return new_group

    def is_compatible(self):
        if self.animal_type == 'female':
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

    def name_get(self):
        displayName = []
        for group in self:
            displayName.append((group.id, group.animal_group.number))
        return displayName
