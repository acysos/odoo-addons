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
                        if party.number == lot and party not in sale_animal:
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
                    elif lot.qty < group.quantity and group.state != 'sold':
                        group.quantity = group.quantity - lot.qty
                        farm_mov_obj = self.env['farm.move.event']
                        farm_mov_obj.create({
                            'animal_type': 'group',
                            'specie': group.specie.id,
                            'farm': group.farm.id,
                            'animal_group': group.id,
                            'timestamp': self.picking_id.date,
                            'from_location': group.location.id,
                            'to_location': self.location_dest_id.id,
                            'quantity': lot.qty,
                            'unit_price': 1,
                            'move': self.id,
                            })
                    else:
                        raise Warning(_('there are insufficient nº of animals'))

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
    _inherit = 'stock.production.lot'

    animal_type = fields.Selection(selection=ANIMAL_TYPE)
    animal_group = fields.One2many(comodel_name='stock.lot_farm.animal.group',
                                   inverse_name='animal_group', string='Group')
    semen_breed = fields.Many2one(comodel_name='farm.specie.breed',
                                  string='Raza')


class LotAnimal(models.Model):
    _name = 'stock.lot_farm.animal'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.production.lot',
                          string='Lot')
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             ondelete='RESTRICT', select=True)


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
    radius = fields.Float(string='Radius', help='is used for calculating '
                          'transport costs, you can use absolute or relative'
                          ' values', default=1)
    animal_max = fields.Integer(string='Max num of animals')


class Location(models.Model):
    _inherit = 'stock.location'

    silo = fields.Boolean(string='Silo', select=True, default=False,
                          help='Indicates that the location is a silo.')
    factory = fields.Boolean(string='Factory', default=False)
    farm_yard = fields.Boolean(string='Farm Yard', select=True, default=False)
    locations_to_fed = fields.One2many(
        comodel_name='stock.location.silo_stock.location',
        inverse_name='silo', string='Location to fed',
        help='Indicates the locations the silo feeds. Note that this will '
        'only be a default value.')
    animal_max = fields.Integer(string='Max num of animals')

    @api.multi
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


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    feed_analitic = fields.Boolean('Set Feed Analitic', default=False)


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.model
    def _resolve_inventory_line(self, inventory_line):
        res = super(
            StockInventoryLine, self)._resolve_inventory_line(
                inventory_line)
        if res:
            move = self.env['stock.move'].search([('id', '=', res)])
            diff = inventory_line.theoretical_qty - inventory_line.product_qty
            if inventory_line.inventory_id.feed_analitic:
                if diff < 0:
                    self.set_analitics(move, False)
                else:
                    self.set_analitics(move, True)
        return res

    @api.multi
    def set_analitics(self, move, lost):
        analitic_remain_ob = self.env['purchase.analitic.remain']
        if lost:
            location = move.location_id
        else:
            location = move.location_dest_id
        factory = location
        while(factory.location_id.id != 1):
            factory = factory.location_id
        analitic_remain = analitic_remain_ob.search([
                                    ('farm', '=', factory.id)])
        lot_cost = move.restrict_lot_id.unit_cost
        qty = move.product_uom_qty
        cost = 0
        if lot_cost and lot_cost > 0:
            cost = lot_cost * qty
        else:
            quants_obj = self.env['stock.quant']
            quants = quants_obj.search([
                ('lot_id', '=', move.restrict_lot_id.id)])
            ids = []
            for q in quants:
                ids.append(q.id)
            moves = self.env['stock.move'].with_context({}).search([
                ('quant_ids', 'in', ids),
                ('picking_id', '!=', False)])
            amount = 0.0
            raw_qty = 0
            for mov in moves:
                if mov.price_unit > 0:
                    amount += mov.price_unit * mov.product_qty
                    raw_qty = raw_qty + mov.product_qty
            if raw_qty > 0:
                unit_price = amount/raw_qty
                cost += qty * unit_price
            if cost == 0:
                prod_tmpl = move.product_id.product_tmpl_id
                cost = prod_tmpl.standard_price * qty
        if not lost:
            cost = cost * -1
        if len(analitic_remain) == 0:
            analitic_remain_ob.create({
                'farm': factory.id,
                'quantity': cost})
        else:
            analitic_remain.quantity = \
                analitic_remain.quantity + cost
