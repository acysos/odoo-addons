# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning

ANIMAL_TYPE = [(None, 'No animal'), ('male', 'Male)'), ('female', 'Female'),
               ('individual', 'Individual'), ('group', 'Group'), ]


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, partner, inv_type, contetx=None):
        res = super(stock_move, self)._get_invoice_line_vals(partner,
                                                             inv_type, contetx)
        specie = self.env['farm.specie'].search([
            (True, '=', True)])[0]
        if len(specie.sale_product) != 0:
            alter_prod = specie.sale_product
            if res['product_id'] == specie.group_product.id or \
                    res['product_id'] == specie.female_product.id or \
                    res['product_id'] == specie.male_product.id:
                            res['product_id'] = alter_prod.id
                            res['uos_id'] = alter_prod.uos_id.id
                            res['quantity'] = 1
                            res['price_unit'] = 1
        return res

    @api.multi
    def action_done(self):
        super(stock_move, self).action_done()
        customer_location = self.env['stock.location'].search([
            ('usage', '=', 'customer')])
        for line in self:
            if customer_location.id == line.location_dest_id.id:
                lots = []
                for lot in line.quant_ids:
                    lots.append(lot.lot_id.name)
                animals_obj = self.env['farm.animal.group']
                partys = animals_obj.search([('state', '!=', 'sold')])
                sale_animal = []
                for party in partys:
                    for lot in lots:
                        if party.number == lot:
                            sale_animal.append(party)
                if len(sale_animal) > 0:
                    self.sale_group(sale_animal)
                else:
                    species_obj = self.env['farm.specie']
                    for specie in species_obj:
                        if line.product_id.id == specie.group_product.id:
                            raise Warning(_('group sold not found'))

    @api.one
    def sale_group(self, groups):
        for group in groups:
            for lot in self.quant_ids:
                if lot.lot_id.name == group.number:
                    if lot.qty == group.quantity:
                        self.totalSale(group, lot.qty)
                    else:
                        group.quantity = group.quantity - lot.qty
                        farm_mov_obj = self.env['farm.move.event']
                        farm_mov_obj.create({
                            'animal_type': 'group',
                            'specie': group.specie.id,
                            'farm': group.farm.id,
                            'animal_group': group.id,
                            'from_location': group.location.id,
                            'to_location': self.location_dest_id.id,
                            'quantity': lot.qty,
                            'unit_price': 1,
                            'move': self.id,
                            })

    @api.one
    def totalSale(self, group, qty):
        group.state = 'sold'
        farm_mov_obj = self.env['farm.move.event']
        if group.quantity < group.initial_quantity:
            old_movs = farm_mov_obj.search([
                ('animal_group', '=', group.id)])
            if len(old_movs) > 0:
                group.quantity = group.initial_quantity
        farm_mov_obj.create({
            'animal_type': 'group',
            'specie': group.specie.id,
            'farm': group.farm.id,
            'animal_group': group.id,
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
    _inherit = 'stock.production.lot'
    animal_type = fields.Selection(selection=ANIMAL_TYPE)
    animal = fields.One2many(comodel_name='stock.lot_farm.animal',
                             inverse_name='animal', string='Animal')
    animal_group = fields.One2many(comodel_name='stock.lot_farm.animal.group',
                                   inverse_name='animal_group', string='Group')
    semen_breed = fields.Many2one(comodel_name='farm.specie.breed',
                                  string='Raza')

class LotAnimal(models.Model):
    _name = 'stock.lot_farm.animal'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.production.lot',
                          string='Lot', ondelete='RESTRICT',
                          select=True)
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             requiered=True, ondelete='RESTRICT', select=True)


class LotAnimalGroup(models.Model):
    _name = 'stock.lot_farm.animal.group'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.production.lot',
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


class Location(models.Model):
    _inherit = 'stock.location'

    silo = fields.Boolean(string='Silo', select=True, default=False,
                          help='Indicates that the location is a silo.')
    farm_yard = fields.Boolean(string='Farm Yard', select=True, default=False)
    locations_to_fed = fields.Many2many(
        comodel_name='stock.location.silo_stock.location',
        column1='location', string='Location to fed',
        domain=[('silo', '=', False),],
        help='Indicates the locations the silo feeds. Note that this will '
        'only be a default value.')


class LocationSiloLocation(models.Model):
    _name = 'stock.location.silo_stock.location'

    silo = fields.Many2one(comodel_name='stock.location', string='silo',
                           ondelete='CASCADE', required=True, select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               ondelete='CASCADE', requiered=True, select=True)


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
