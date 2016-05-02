# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime


DFORMAT = "%Y-%m-%d %H:%M:%S"


class AnimalGroup(models.Model):
    _name = 'farm.animal.group'
    _order = 'arrival_date desc'

    mother = fields.Char(string='Mother', compute='get_mother')
    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             required=True)
    breed = fields.Many2one(comodel_name='farm.specie.breed', string='Breed',
                            required=True)
    lot = fields.One2many(comodel_name='stock.lot_farm.animal.group',
                          inverse_name='animal_group', column1='lot',
                          string='Lot')
    number = fields.Char(string='Number', compute='get_number')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Current location',
                               domain=[('usage', '=', 'internal'), ])
    farm = fields.Many2one(comodel_name='stock.location',
                           string='Current Farm',
                           domain=[('usage', '=', 'view')])
    quantity = fields.Integer(string='Quantity')
    origin = fields.Selection([('purchased', 'Purchased'),
                               ('raised', 'Raised'), ], string='Origin',
                              required=True,
                              default='purchased',
                              help='Raised means that this group was born in'
                              'the farm. Otherwise, it was purchased.')
    arrival_date = fields.Date(string='Arrival Date',
                               default=fields.Date.today(),
                               help="The date this group arrived (if it was"
                               "purchased) or when it was born.")
    """
    purchase_shipment = fields.Many2one(comodel_name='stock.shipment.in',
                                       string='Purchase Shipment',
                                       readonly=True)
    """
    initial_location = fields.Many2one(comodel_name='stock.location',
                                       string='Initial location',
                                       required=True,
                                       domain=[('usage', '=', 'internal'),
                                               ('silo', '=', False), ],
                                       help="The Location where the group was"
                                       "reached or where it was allocated when"
                                       "it was purchased.\nIt is used as"
                                       "historical information and to get"
                                       "Serial Number.")
    initial_quantity = fields.Integer(string='Initial quantity', required=True,
                                      help="The number of animals in group"
                                      "when it was reached or purchased.\nIt"
                                      "is used as historical information and"
                                      "to create the initial move.")
    removal_date = fields.Date(string='Removal date', readonly=True)
    weights = fields.One2many(comodel_name='farm.animal.group.weight',
                              inverse_name='party', column1='tag',
                              string='Weights')
    current_weight = fields.Many2one(comodel_name='farm.animal.group.weight',
                                     string='Current weight',
                                     compute='on_change_with_current_weight')
    tags = fields.Many2many(comodel_name='farm.tags',
                            inverse_name='animal_group', string='Tag')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    feed_quantity = fields.Float(string='cumulative consumed feed')
    consumed_feed = fields.Float(string='Consumed Feed per Animal (kg)',
                                 compute='get_consumed_feed')
    state = fields.Selection(selection=[
        ('lactating', 'Lactating'), ('transition', 'Transition'),
        ('fatten', 'Faten up'), ('sold', 'Sold')],
        readonly=True, default='fatten')
    transition_days = fields.Integer(string='Days in Transition',
                                     compute='get_transit_days')
    fattening_days = fields.Integer(string='Days in fatening',
                                    compute='get_fattenig_days')
    account = fields.Many2one(comodel_name='account.analytic.account',
                              string='Analytic Account')
    weaning_day = fields.Datetime(string='weaning_day', compute='get_weaning_day')
    
    @api.multi
    def get_mother(self):
        farrow = self.env['farm.farrowing.event_group']
        for res in self:
            group_farrow = farrow.search([
                ('animal_group', '=', res.id)])
            if len(group_farrow)!= 0:
                res.mother = group_farrow.event.animal.ifr_sequence
            else:
                res.mother = '*'

    @api.one
    def get_weaning_day(self):
        if self.state != 'lactating':
            weaning_obj = self.env['farm.weaning.event']
            wean = weaning_obj.search([
                ('farrowing_group', '=', self.id)])
            if len(wean) != 0:
                self.weaning_day = datetime.strptime(wean.timestamp, DFORMAT)
    
    @api.one
    def get_transit_days(self):
        if self.state == 'lactating':
            self.transition_days = 0
        elif self.state == 'transition':
            weaning_obj = self.env['farm.weaning.event']
            wean = weaning_obj.search([
                ('farrowing_group', '=', self.id)])
            wean_day = datetime.strptime(wean.timestamp, DFORMAT)
            self.transition_days = (datetime.today() - wean_day).days
        else:
            weaning_obj = self.env['farm.weaning.event']
            transformation_obj = self.env['farm.transformation.event']
            wean = weaning_obj.search([
                ('farrowing_group', '=', self.id)])
            if len(wean) != 0:
                transition_location = []
                for loc in self.specie.lost_found_location:
                    transition_location.append(loc.location.id)
                transition = transformation_obj.search([
                    ('animal_group', '=', self.id),
                    ('from_location.id', 'in', transition_location),
                    ('to_location.id', 'not in', transition_location)])
                wean_day = datetime.strptime(wean.timestamp, DFORMAT)
                transition_finish = datetime.strptime(
                    transition.timestamp, DFORMAT)
                self.transition_days = (transition_finish - wean_day).days
            else:
                self.transition_days = 0

    @api.one
    def get_fattenig_days(self):
        if self.state == 'lactating' or self.state == 'transition':
            self.fattening_days = 0
        else:
            transformation_obj = self.env['farm.transformation.event']
            transition_location = []
            for loc in self.specie.lost_found_location:
                transition_location.append(loc.location.id)
            transition = transformation_obj.search([
                ('animal_group', '=', self.id),
                ('from_location.id', 'in', transition_location),
                ('to_location.id', 'not in', transition_location)])
            if len(transition) == 0:
                transition_finish = datetime.strptime(
                    self.arrival_date, '%Y-%m-%d')
            else:
                transition_finish = datetime.strptime(
                    transition.timestamp, DFORMAT)
            if self.state == 'fatten':
                self.fattening_days = (
                    datetime.today() - transition_finish).days
            else:
                moves_obj = self.env['farm.move.event']
                sale_move = moves_obj.search([
                    ('animal_group', '=', self.id)])
                sale_day = datetime.strptime(
                    sale_move[-1].timestamp, DFORMAT)
                self.fattening_days = (sale_day - transition_finish).days

    @api.multi
    def create_first_move(self, res):
        moves_obj = self.env['stock.move']
        quant_obj = self.env['stock.quant']
        for record in res:
            if not record.lot:
                        production_lot_obj = self.env['stock.production.lot']
                        animal_group_lot_obj = \
                            self.env['stock.lot_farm.animal.group']
                        new_lot = production_lot_obj.create({
                            'product_id': res.specie.group_product.id,
                            'animal_type': 'group',
                            })
                        animal_group_lot_obj.create({
                            'lot': new_lot.id,
                            'animal_group': res.id})
            quant = quant_obj.search([(
                'lot_id', '=', record.lot[0].lot.id)])
            record.location = record.initial_location
            if len(record.lot) > 1:
                    raise Warning(
                        _('lots can not be mixed in an initial group, create a'
                          ' group for each lot and then group them into the'
                          ' desired group'))
            elif record.origin == 'raised':
                if not quant:
                    raise_location = self.env['stock.location'].search(
                        [('usage', '=', 'production')])
                    uom = record.lot.lot.product_id.product_tmpl_id.uom_id.id
                    new_move = moves_obj.create({
                        'name': 'raise-' + record.lot[0].lot.name,
                        'create_date': fields.Date.today(),
                        'date': record.arrival_date,
                        'product_id': record.lot[0].lot.product_id.id,
                        'product_uom_qty': record.initial_quantity,
                        'product_uom': uom,
                        'location_id': raise_location.id,
                        'location_dest_id': record.initial_location.id,
                        'company_id': record.initial_location.company_id.id,
                        })
                    new_move.action_done()
                    new_move.quant_ids.lot_id = record.lot[0].lot.id
                    self.stock_move = new_move
                else:
                    raise Warning(
                        _('this lot iis in use, please create new lot'))
            else:
                if not quant:
                    raise Warning(
                        _('no product in farms for this lot'))
                elif quant.location_id != record.initial_location:
                    raise Warning(
                        _('group location and product location are diferent'))
                elif quant.qty != record.initial_quantity:
                    raise Warning(
                        _('group intial quantity and product quantity '
                          'are diferent'))
                an_group = self.env['farm.animal.group'].search([
                    ('lot.lot.id', '=', record.lot.lot.id),
                    ('id', '!=', record.id)])
                if len(an_group) > 0:
                    raise Warning(
                        _('this lot is in use from oder group'))
                current_move = moves_obj.search([
                    ('quant_ids.id', '=', record.lot.lot.id)])
                self.stock_move = current_move

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(AnimalGroup, self).create(vals)
        self.create_first_move(res)
        res.quantity = res.initial_quantity
        analy_ac_obj = self.env['account.analytic.account']
        new_account = analy_ac_obj.create({
            'name': 'AA-group-'+res.number})
        res.account = new_account
        return res

    @api.multi
    def name_get(self):
        result = ''
        displayName = []
        for group in self:
            if group.tags:
                displayName.append(
                    (group.id, group.number + '-' +group.tags[0].name))
            else:
                displayName.append((group.id, group.number))
        return displayName

    def get_number(self):
        for group in self:
            result = '*'
            if len(group.lot) > 2:
                result = group.lot[2].lot.name
            elif len(group.lot) > 0:
                result = group.lot[0].lot.name
            group.number = result

    def get_locations(self):
        return False

    @api.one
    def on_change_with_current_weight(self):
        if self.weights:
            self.current_weight = self.weights[0].id

    @api.one
    def get_consumed_feed(self):
        if self.feed_quantity == 0 or self.quantity == 0:
            self.consumed_feed = 0
        else:
            self.consumed_feed = self.feed_quantity/self.quantity


class AnimalGroupWeight(models.Model):
    _name = 'farm.animal.group.weight'
    _order = 'timestamp DESC'
    rec_name = 'weight'

    party = fields.Many2one(comodel_name='farm.animal.group',
                            string='Group', ondelete='CASCADE',
                            required=True)
    timestamp = fields.Datetime(string='Date & time',
                                default=fields.Datetime.now())
    quantity = fields.Integer(string='Number of individuals', required=True)
    uom = fields.Many2one(comodel_name='product.uom', string='Uom')
    weight = fields.Float(string='Weihht', digits=(3, 2))

    @api.onchange('timestamp')
    def get_defaults(self):
        if self.party is not False:
            self.quantity = self.party.quantity
