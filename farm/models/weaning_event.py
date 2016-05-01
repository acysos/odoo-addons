# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


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
                                         domain=[('usage', '=', 'transit'),
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

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(WeaningEvent, self).create(vals)
        res.get_quantity()
        return res

    @api.one
    @api.onchange('animal')
    def onchange_animal(self):
        c_c = self.animal.current_cycle
        self.weared_group = \
            c_c.farrowing_event.event.produced_group.animal_group

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise Warning(
                _("Only females can wean a group"))
        if not self.is_ready():
            raise Warning(
                _("Only lactating females can wean a group"))
        far_event = self.animal.current_cycle.farrowing_event
        self.farrowing_group = \
            far_event.event.produced_group.animal_group
        wean_fem_cy_obj = self.env['farm.weaning.event_female_cycle']
        wean_fem_cy_obj.create({
            'event': self.id,
            'cycle': self.animal.current_cycle.id, })
        self.get_female_move()
        if self.farrowing_group == self.weared_group:
                self.move_group()
        else:
            self.trasform_group()
        self.animal.current_cycle.update_state(self)
        self.farrowing_group.state = 'transition'
        for line in self.animal.account.line_ids:
            line.account_id = self.weared_group.account
            line.name = 'wean Cost'
        super(WeaningEvent, self).confirm()

    @api.one
    def move_group(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        f_g = self.farrowing_group
        target_quant = quants_obj.search([
            ('lot_id', '=', f_g.lot.lot.id),
            ('location_id', '=', f_g.location.id),
            ])
        f_g_move = moves_obj.create({
            'name': 'wean-' + f_g.number,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': f_g.lot.lot.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom':
                f_g.lot.lot.product_id.product_tmpl_id.uom_id.id,
            'location_id': f_g.location.id,
            'location_dest_id': self.weaned_to_location.id,
            'company_id': self.animal.farm.company_id.id, })
        for q in target_quant:
            q.reservation_id = f_g_move.id
        f_g_move.action_done()
        self.weared_move = f_g_move
        f_g.location = self.weaned_to_location
        tags_obj = self.env['farm.tags']
        tag = tags_obj.search([
                ('name', '=', self.farm.name + '-lact')])
        tag.animal_group = [(3, self.farrowing_group.id)]
        new_tag = tags_obj.search([
            ('name', '=', self.farm.name + '-transi')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': self.farm.name + '-transi',
                                       })
        self.farrowing_group.tags = [(6, 0, [new_tag.id, ])]

    @api.one
    def trasform_group(self):
        if self.quantity == self.farrowing_group.quantity:
            self.get_female_move()
        trans_eve_obj = self.env['farm.transformation.event']
        new_trans_ev = trans_eve_obj.create({
            'animal_type': 'group',
            'specie': self.specie.id,
            'farm': self.farm.id,
            'animal_group': self.farrowing_group.id,
            'timestamp': self.timestamp,
            'from_location': self.farrowing_group.location.id,
            'to_animal_type': 'group',
            'to_location': self.weaned_to_location.id,
            'quantity': self.quantity,
            'to_animal_group': self.weared_group.id,
            })
        new_trans_ev.confirm()
        self.transformation_event = new_trans_ev
        self.weared_move = new_trans_ev.move

    @api.one
    def get_female_move(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        target_quant = quants_obj.search([
            ('lot_id', '=', self.animal.lot.lot.id),
            ('location_id', '=', self.animal.location.id),
            ])
        fem_move = moves_obj.create({
            'name': 'wean-mother-' + self.animal.lot.lot.name,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': self.animal.lot.lot.product_id.id,
            'product_uom_qty': 1,
            'product_uom':
                self.animal.lot.lot.product_id.product_tmpl_id.uom_id.id,
            'location_id': self.animal.location.id,
            'location_dest_id': self.female_to_location.id,
            'company_id': self.animal.farm.company_id.id, })
        for q in target_quant:
            q.reservation_id = fem_move.id
        fem_move.action_done()
        self.female_move = fem_move
        self.animal.location = self.female_to_location
        tags_obj = self.env['farm.tags']
        tag = tags_obj.search([
                ('name', '=', self.farm.name+'-lact')])
        tag.animal = [(3, self.animal.id)]
        new_tag = tags_obj.search([
            ('name', '=', self.farm.name + '-unmated')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': self.farm.name + '-unmated',
                                       })
        self.animal.tags = [(6, 0, [new_tag.id, ])]

    @api.one
    def get_farrowing_group(self):
        self.farrowing_group = \
            self.animal.current_cycle.farrowing_event.event.produced_group

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

    @api.one
    def get_quantity(self):
        far_event = self.animal.current_cycle.farrowing_event
        farrowing_group = far_event.event.produced_group.animal_group
        self.quantity = farrowing_group.quantity


class WearingEventFemaleCycle(models.Model):
    _name = 'farm.weaning.event_female_cycle'

    event = fields.Many2one(comodel_name='farm.weaning.event',
                            string='Wearing Event', required=True,
                            ondelete='RESTRICT')
    cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                            string='Female Cycle', required=True,
                            ondelete='RESTRICT')
