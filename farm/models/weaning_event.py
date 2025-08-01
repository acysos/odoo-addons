# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning


class WeaningEvent(models.Model):
    _name = 'farm.weaning.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}
    _auto = True

    farrowing_group = fields.Many2one(comodel_name='farm.animal.group',
                                      string='Farrowing Group')
    quantity = fields.Integer(string='Quantity', compute='get_quantity',
                              store=True)
    female_to_location = fields.Many2one(comodel_name='stock.location',
                                         string='Female Destination',
                                         required=True,
                                         domain=[('usage', '=', 'internal'),
                                                 ('silo', '=', False)])
    weaned_to_location = fields.Many2one(comodel_name='stock.location',
                                         string='Weaned Destination',
                                         required=True,
                                         domain=[
                                                 ('silo', '=', False)])
    weared_group = fields.Many2one(comodel_name='farm.animal.group',
                                   string='Weaned group',
                                   help='Group in which weaned animals should'
                                   'be added to. If left blank they will keep'
                                   'the same group.')
    female_cycle = fields.One2many(
        comodel_name='farm.weaning.event_female_cycle',
        inverse_name='event', column1='cycle', string='Female Cicle',
        readonly=True)
    female_move = fields.Many2one(comodel_name='stock.move',
                                  string='Female Stock Move')
    lost_move = fields.Many2one(comodel_name='stock.move',
                                string='Lost Stock  Move')
    weared_move = fields.Many2one(comodel_name='stock.move',
                                  string='Weared Stock Move')
    transformation_event = fields.Many2one(
        comodel_name='farm.transformation.event',
        string='Transformation Event')

    @api.model_create_multi
    def create(self, vals):
        res = super(WeaningEvent, self).create(vals)
        res.get_quantity()
        return res

    @api.onchange('animal')
    def onchange_animal(self):
        c_c = self.animal.current_cycle
        self.weared_group = \
            c_c.farrowing_event.event.produced_group.animal_group

    def confirm(self):
        for res in self:
            if not res.is_compatible():
                raise Warning(
                    _("Only females can wean a group"))
            if not res.is_ready():
                raise Warning(
                    _("Only lactating females can wean a group"))

            far_event = res.animal.current_cycle.farrowing_event
            res.farrowing_group = \
                far_event.event.produced_group.animal_group
            wean_fem_cy_obj = self.env['farm.weaning.event_female_cycle']
            wean_fem_cy_obj.create({
                'event': res.id,
                'cycle': res.animal.current_cycle.id, })
            res.get_female_move()
            if res.farrowing_group.quantity > 0:
                if res.farrowing_group == res.weared_group:
                        res.move_group()
                else:
                    res.trasform_group()
                res.animal.current_cycle.update_state(self)
                res.farrowing_group.state = 'transition'

            res.animal.current_cycle.update_state(res)
        super(WeaningEvent, self).confirm()

    def move_group(self):
        for res in self:
            moves_obj = self.env['stock.move']
            quants_obj = self.env['stock.quant']
            f_g = res.farrowing_group
            target_quant = quants_obj.search([
                ('lot_id', '=', f_g.lot.lot.id),
                ('location_id', '=', f_g.location.id),
                ])
            f_g_move = moves_obj.create({
                'name': 'wean-' + f_g.number,
                'create_date': fields.Date.today(),
                'date': res.timestamp,
                'product_id': f_g.lot.lot.product_id.id,
                'product_uom_qty': res.quantity,
                'product_uom':
                    f_g.lot.lot.product_id.product_tmpl_id.uom_id.id,
                'location_id': f_g.location.id,
                'location_dest_id': res.weaned_to_location.id,
                'company_id': res.animal.farm.company_id.id, })
            for q in target_quant:
                q.reservation_id = f_g_move.id
            f_g_move.action_done()
            res.weared_move = f_g_move
            f_g.location = res.weaned_to_location
            tags_obj = res.env['farm.tags']
            tag = tags_obj.search([
                    ('name', '=', res.farm.name + '-lact')])
            tag.animal_group = [(3, res.farrowing_group.id)]
            new_tag = tags_obj.search([
                ('name', '=', res.farm.name + '-transi')])
            if len(new_tag) == 0:
                new_tag = tags_obj.create({'name': res.farm.name + '-transi',
                                           })
            res.farrowing_group.tags = [(6, 0, [new_tag.id, ])]

    def trasform_group(self):
        for res in self:
            if res.quantity == res.farrowing_group.quantity:
                res.get_female_move()
            trans_eve_obj = self.env['farm.transformation.event']
            new_trans_ev = trans_eve_obj.create({
                'animal_type': 'group',
                'specie': res.specie.id,
                'farm': res.farm.id,
                'animal_group': res.farrowing_group.id,
                'timestamp': res.timestamp,
                'from_location': res.farrowing_group.location.id,
                'to_animal_type': 'group',
                'to_location': res.weaned_to_location.id,
                'quantity': res.quantity,
                'to_animal_group': res.weared_group.id,
                })
            new_trans_ev.confirm()
            res.transformation_event = new_trans_ev
            res.weared_move = new_trans_ev.move

    def get_female_move(self):
        for res in self:
            moves_obj = self.env['stock.move']
            quants_obj = self.env['stock.quant']
            target_quant = quants_obj.search([
                ('lot_id', '=', res.animal.lot.lot.id),
                ('location_id', '=', res.animal.location.id),
                ])
            fem_move = moves_obj.create({
                'name': 'wean-mother-' + res.animal.lot.lot.name,
                'create_date': fields.Date.today(),
                'date': res.timestamp,
                'product_id': res.animal.lot.lot.product_id.id,
                'product_uom_qty': 1,
                'product_uom':
                    res.animal.lot.lot.product_id.product_tmpl_id.uom_id.id,
                'location_id': res.animal.location.id,
                'location_dest_id': res.female_to_location.id,
                'company_id': res.animal.farm.company_id.id, })
            for q in target_quant:
                q.reservation_id = fem_move.id
            fem_move.action_done()
            res.female_move = fem_move
            res.animal.location = res.female_to_location
            tags_obj = res.env['farm.tags']
            tag = tags_obj.search([
                    ('name', '=', res.farm.name+'-lact')])
            tag.animal = [(3, res.animal.id)]
            new_tag = tags_obj.search([
                ('name', '=', res.farm.name + '-unmated')])
            if len(new_tag) == 0:
                new_tag = tags_obj.create({'name': res.farm.name + '-unmated',
                                           })
            self.animal.tags = [(6, 0, [new_tag.id, ])]

    def get_farrowing_group(self):
        for res in self:
            res.farrowing_group = \
                res.animal.current_cycle.farrowing_event.event.produced_group

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.animal.current_cycle.state == 'lactating':
            return True
        else:
            return False

    def get_quantity(self):
        for res in self:
            far_event = res.animal.current_cycle.farrowing_event
            farrowing_group = far_event.event.produced_group.animal_group
            res.quantity = farrowing_group.quantity


class WearingEventFemaleCycle(models.Model):
    _name = 'farm.weaning.event_female_cycle'

    event = fields.Many2one(comodel_name='farm.weaning.event',
                            string='Wearing Event', required=True,
                            ondelete='RESTRICT')
    cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                            string='Female Cycle', required=True,
                            ondelete='RESTRICT')
