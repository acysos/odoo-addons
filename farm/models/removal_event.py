# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class RemovalType(models.Model):
    _name = 'farm.removal.type'

    name = fields.Char(string='Name', required=True, traslate=True)


class RemovalReason(models.Model):
    _name = 'farm.removal.reason'

    name = fields.Char(string='Name', required=True, traslate=True)


class RemovalEvent(models.Model):
    _name = 'farm.removal.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}
    _auto = True

    from_location = fields.Many2one(comodel_name='stock.location',
                                    string='Origin', required=True,
                                    domain=[('silo', '=', False), ])
    quantity = fields.Integer(string='Quantity', required=True,
                              default=1)
    removal_type = fields.Many2one(comodel_name='farm.removal.type',
                                   string='Type')
    reason = fields.Many2one(comodel_name='farm.removal.reason',
                             string='Reason')
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move')
    specific_lot = fields.Many2one(comodel_name='stock.production_lot',
                                   string='Specific lot')

    @api.one
    @api.onchange('animal', 'animal_group')
    def get_from_location(self):
        if self.animal_type == 'group':
            self.from_location = self.animal_group.location
            self.quantity = self.animal_group.quantity
        else:
            self.from_location = self.animal.location

    @api.one
    def confirm(self):
        if not self.is_compatible_quant():
            return False
        elif not self.is_compatible_to_location():
            return False
        if self.animal_type == 'group':
            self.remove_group()
        else:
            self.remove_animal()
        super(RemovalEvent, self).confirm()

    @api.one
    def remove_group(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        scrap_loc = self.env['stock.location'].search([
            ('scrap_location', '=', True)])[0]
        if len(self.specific_lot) == 0:
            if len(self.animal_group.lot) < 3:
                lot = self.animal_group.lot[0].lot
            else:
                lot = self.animal_group.lot[2].lot
        else:
            lot = self.specific_lot
        target_quant = quants_obj.search([
            ('lot_id', '=', lot.id),
            ('location_id', '=', self.from_location.id),
            ])
        product_uom = \
            lot.product_id.product_tmpl_id.uom_id.id
        new_move = moves_obj.create({
            'name': 'remove-' + self.animal_group.number,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': lot.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': product_uom,
            'location_id': self.from_location.id,
            'location_dest_id': scrap_loc.id,
            'company_id': self.animal_group.initial_location.company_id.id,
            'origin': self.animal_group.number,
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        self.move = new_move
        self.animal_group.quantity -= self.quantity
        if self.animal_group.quantity < 1:
            self.animal_group.removal_date = self.timestamp

    @api.one
    def remove_animal(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        scrap_loc = self.env['stock.location'].search([
            ('scrap_location', '=', True)])[0]
        target_quant = quants_obj.search([
            ('lot_id', '=', self.animal.lot.lot.id),
            ('location_id', '=', self.from_location.id),
            ])
        product_uom = \
            self.animal.lot.lot.product_id.product_tmpl_id.uom_id.id
        new_move = moves_obj.create({
            'name': 'remove-' + self.animal.number,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': self.animal.lot.lot.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': product_uom,
            'location_id': self.from_location.id,
            'location_dest_id': scrap_loc.id,
            'company_id': self.animal.location.company_id.id,
            'origin': self.animal.lot.lot.name,
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        self.animal.removal_date = self.timestamp
        self.animal.removal_reason = self.reason
        self.animal.active = False
        self.move = new_move

    def is_compatible_quant(self):
        if self.animal_type == 'individual' or \
            self.animal_type == 'male' or \
                self.animal_type == 'female':
            if self.quantity != 1 or self.quantity < 1:
                raise Warning(
                    _('Quantity no compatible'))
        elif self.quantity > self.animal_group.quantity or self.quantity < 1:
            raise Warning(
                _('Quantity no compatible'))
        return True

    def is_compatible_to_location(self):
        if self.animal_type == 'group':
            if self.animal_group.location.id != self.from_location.id:
                raise Warning(
                    _('the origin is different from the location of'
                      ' the group'))
        else:
            if self.animal.location.id != self.from_location.id:
                raise Warning(
                    _('the origin is different from the location of'
                      ' the animal'))
        return True
