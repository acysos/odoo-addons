# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields

INVENTORY_STATES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ('cancel', 'Cancelled'),
    ]


class FeedInventoryMixin(models.Model):
    _name = 'farm.feed.inventory.mixin'
    _auto = False

    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             required=True, select=True)
    location = fields.Many2one(comodel_name='stock.location', string='Silo',
                               required=True, domain=[('silo', '=', True)])
    dest_locations = fields.Many2many(comodel_name='farm.feed.stock.location',
                                      inverse_name='inventory',
                                      column1='location',
                                      string='Location to feed')
    timestamp = fields.Datetime(string='Date & Time', required=True,
                                default=fields.Datetime.now())
    uom = fields.Many2one(comodel_name='product.uom', string='UOM')
    quantity = fields.Float(string='Quantity', digits=(16, 2), required=True)
    feed_events = fields.One2many(comodel_name='farm.feed.event',
                                  inverse_name='feed_inventory',
                                  string='Feed Events', readonly=True)
    state = fields.Selection(selection=INVENTORY_STATES, string='States',
                             required=True, readonly=True, select=True,
                             default='draft')


class FeedInventoryLocation(models.Model):
    _name = 'farm.feed.stock.location'

    inventory = fields.Selection(string='Inventory',
                                 selection='get_inventory', required=True,
                                 select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location', required=True, select=True)

    def get_inventory(self):
        irModel_obj = self.env['ir.model']
        varModels = irModel_obj.search([
            ('model', 'in', ['farm.feed.inventory',
                             'farm.feed.provisional_inventory']), ])
        return [(m.model, m.name) for m in varModels]


class FeedInventory(models.Model):
    _name = 'farm.feed.inventory'
    _inherit = {'farm.feed.inventory.mixin': 'FeedInventoryMixin_id'}
    _auto = True

    prev_inventory = fields.Many2one(comodel_name='farm.feed.inventory',
                                     string='Previous Inventory',
                                     readonly=True)


class FeedProvisionalInventory(models.Model):
    _name = 'farm.feed.provisional_inventory'
    _inherit = {'farm.feed.inventory.mixin': 'FeedInventoryMixin_id'}
    _auto = True

    prev_inventory_date = fields.Date(string='Previous Inventory Date',
                                      readonly=True,
                                      computed='get_previous_inventory_date')
    inventory = fields.Many2one(comodel_name='farm.feed.inventory',
                                string='Inventory', readonly=True)

    def get_previous_inventory_date(self):
        inventory_obj = self.env['farm.feed.inventory']

        prev_inventories = inventory_obj.search([
            ('location', '=', self.location.id),
            ('timestamp', '<', self.timestamp),
            ('state', '=', 'validated'), ],
            order=[('timestamp', 'DESC'), ],
            limit=1)
        if not prev_inventories:
            return None

        prev_prov_inventories = self.search([
            ('location', '=', self.location.id),
            ('timestamp', '<', self.timestamp),
            ('timestamp', '>', prev_inventories[0].timestamp),
            ('state', '=', 'validated'),
            ],
            order=[('timestamp', 'DESC'), ], limit=1)
        if prev_prov_inventories:
            return prev_prov_inventories[0].timestamp.date()
        return prev_inventories[0].timestamp.date()


class FeedAnimalLocationDate(models.Model):
    _name = 'farm.feed.animal_location_date'
    _order = [('location', 'ASC'), ('date', 'DESC'), ]

    animal_type = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('individual', 'Individual'),
        ('group', 'Group'),
        ], "Animal Type", required=True, readonly=True, select=True)
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal')
    animal_group = fields.Many2one(comodel_name='farm.animal.group',
                                   string='Group', select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location fed', select=True)
    animale_qty = fields.Integer(string='Num. Animals')
    date = fields.Date('Date', select=True)
    consumed_qty_animal = fields.Float(string='Consumed Qty, per Animal',
                                       digits=(16, 2), select=True)
    consumed_qty = fields.Float(string='Consumed Qty', digits=(16, 2))
    inventory_qty = fields.Integer(string='Inventoryes',
                                   help='Number of Inventories which include'
                                   'this date.')
