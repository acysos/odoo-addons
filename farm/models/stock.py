# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning

ANIMAL_TYPE = [('No', 'No animal'), ('male', 'Male)'), ('female', 'Female'),
               ('individual', 'Individual'), ('group', 'Group'), ]


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, move, inv_type, contetx=None):
        res = super(stock_move, self)._get_invoice_line_vals(move,
                                                             inv_type, contetx)
        specie = self.env['farm.specie'].search([
            (True, '=', True)])[0]
        if len(specie.sale_product) != 0:
            alter_prod = specie.sale_product
            if res['product_id'] == specie.group_product.id or \
                    res['product_id'] == specie.female_product.id or \
                    res['product_id'] == specie.male_product.id:
                            res['animal_qty'] = res['quantity']
                            res['product_id'] = alter_prod.id
                            res['uos_id'] = alter_prod.uos_id.id
                            res['quantity'] = 1
                            farm = move.location_id.get_farm_warehouse().id
                            res['farm'] = farm

        return res

    def _action_done(self, cancel_backorder=False):
        result = super(stock_move, self)._action_done(cancel_backorder)
        customer_location = self.env['stock.location'].search([
            ('usage', '=', 'customer')])
        for line in self:
            if customer_location.id == line.location_dest_id.id:
                lots = []
                for m_line in line.move_line_ids:
                    lots.append(m_line.lot_id.name)
                animals_obj = self.env['farm.animal.group']
                partys = animals_obj.search([
                    ('state', '!=', 'sold'),
                    ('location', 'child_of', line.location_id.id)])
                sale_animal = []
                for party in partys:
                    for lot in lots:
                        if party.number == lot and party not in sale_animal:
                            sale_animal.append(party)
                if len(sale_animal) > 0:
                    self.sale_group(sale_animal)
                else:
                    species_obj = self.env['farm.specie'].search(
                        [(True, '=', True)])
                    for specie in species_obj:
                        if line.product_id.id == specie.group_product.id:
                            raise Warning(_('group sold not found'))
        return result

    def sale_group(self, groups):
        for group in groups:
            for m_line in self.move_line_ids:
                if m_line.lot_id.name == group.number:
                    if m_line.quantity == group.quantity:
                        self.totalSale(group, lot.qty)
                    elif m_line.quantity < group.quantity and group.state != 'sold':
                        group.quantity = group.quantity - m_line.quantity
                        farm_mov_obj = self.env['farm.move.event']
                        farm_mov_obj.create({
                            'animal_type': 'group',
                            'specie': group.specie.id,
                            'farm': group.farm.id,
                            'animal_group': group.id,
                            'timestamp': self.picking_id.date,
                            'from_location': group.location.id,
                            'to_location': self.location_dest_id.id,
                            'quantity': m_line.quantity,
                            'unit_price': 1,
                            'move': self.id,
                        })
                    else:
                        raise Warning(
                            _('there are insufficient nº of animals'))

    def totalSale(self, group, qty):
        group.state = 'sold'
        group.removal_date = self.date
        farm_mov_obj = self.env['farm.move.event']
        group.quantity = 0
        farm_mov_obj.create({
            'animal_type': 'group',
            'specie': group.specie.id,
            'farm': group.farm.id,
            'animal_group': group.id,
            'timestamp': self.picking_id.date,
            'from_location': group.location.id,
            'to_location': self.location_dest_id.id,
            'quantity': qty,
            'unit_price': 1,
            'move': self.id,
            })
        tags_obj = self.env['farm.tags']
        new_tag = tags_obj.search([
            ('name', '=', group.farm.name + '-Sold')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create(
                {'name': group.farm.name + '-Sold', })
        group.tags = [(6, 0, [new_tag.id, ])]


class Lot(models.Model):
    _inherit = 'stock.lot'

    animal_type = fields.Selection(selection=ANIMAL_TYPE, default='No',)
    animal_group = fields.One2many(comodel_name='stock.lot_farm.animal.group',
                                   inverse_name='animal_group', string='Group')
    semen_breed = fields.Many2one(comodel_name='farm.specie.breed',
                                  string='Raza')


class LotAnimal(models.Model):
    _name = 'stock.lot_farm.animal'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.lot',
                          string='Lot')
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             ondelete='RESTRICT')


class LotAnimalGroup(models.Model):
    _name = 'stock.lot_farm.animal.group'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.lot',
                          string='Lot', required=True,
                          ondelete='RESTRICT', select=True)
    animal_group = fields.Many2one(
        comodel_name='farm.animal.group',
        string='Animal Group', required=True,
        ondelete='RESTRICT', select=True)


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    external = fields.Boolean(String='External Farm')
    holding_number = fields.Char(string='holding number')
    radius = fields.Float(string='Radius', help='is used for calculating '
                          'transport costs, you can use absolute or relative'
                          ' values', default=1)
    animal_max = fields.Integer(string='Max num of animals')


class Location(models.Model):
    _inherit = 'stock.location'

    silo = fields.Boolean(string='Silo', default=False,
                          help='Indicates that the location is a silo.')
    factory = fields.Boolean(string='Factory', default=False)
    transport = fields.Boolean(string='Transport', default=False)
    farm_yard = fields.Boolean(string='Farm Yard', default=False)
    locations_to_fed = fields.One2many(
        comodel_name='stock.location.silo_stock.location',
        inverse_name='silo', string='Location to fed',
        help='Indicates the locations the silo feeds. Note that this will '
        'only be a default value.')
    animal_max = fields.Integer(string='Max num of animals')

    def get_farm_warehouse(self):
        for res in self:
            view_loc = res
            while view_loc.usage != 'view':
                view_loc = view_loc.location_id
            warehouse = self.env['stock.warehouse'].search([
                ('view_location_id', '=', view_loc.id)])
        return warehouse


class LocationSiloLocation(models.Model):
    _name = 'stock.location.silo_stock.location'

    silo = fields.Many2one(comodel_name='stock.location', string='silo',
                           ondelete='CASCADE', required=True, select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               ondelete='CASCADE', required=True, select=True)


class Foster_location_stock(models.Model):
    _name = 'farm.foster.locations'
    _rec_name = 'location'

    specie = fields.Many2one(comodel_name='farm.specie', string='specie')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'transit')])


class Transit_location_stock(models.Model):
    _name = 'farm.transit.locations'
    _rec_name = 'location'

    specie = fields.Many2one(comodel_name='farm.specie', string='specie')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'transit')])


class Future_maders_location_stock(models.Model):
    _name = 'farm.future_maders.locations'
    _rec_name = 'location'

    specie = fields.Many2one(comodel_name='farm.specie', string='specie')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'transit')])
