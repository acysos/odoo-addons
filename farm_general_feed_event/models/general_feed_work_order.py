# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2025  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning


EVENT_STATES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ]
DISTRIBUTION_TYPES = [
    ('farm', 'Farm'), ('yard', 'Yard')]


class GeneralFeedEventOrder(models.Model):
    _name = 'farm.general.feed.event'

    name = fields.Char(string='Reference', select=True, required=True)
    state = fields.Selection(string='State', selection=EVENT_STATES,
                             default='draft')
    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             select=True, required=True)
    farm = fields.Many2one(comodel_name='stock.location', string='Farm',
                           required=True,
                           domain=[('usage', '=', 'view'), ])
    distribution_type = fields.Selection(string='Distribution Type',
                                         selection=DISTRIBUTION_TYPES,
                                         default='yard')
    location_dest = fields.Many2one(comodel_name='stock.location',
                                    string='Feed destity location',
                                    required=True)
    dest_yard = fields.Many2one(comodel_name='stock.location', string='Yard')
    timestamp = fields.Datetime(string='Date & Time', requiered=True,
                                default=fields.Datetime.now())
    employee = fields.Many2one(comodel_name='res.users', string='Employee',
                               help='Employee that did the job.')
    job_order = fields.Many2one(comodel_name='farm.event.order')
    notes = fields.Text(string='Notes')
    feed_location = fields.Many2one(comodel_name='stock.location',
                                    string='Feed Source', required=True)
    feed_product = fields.Many2one(comodel_name='product.product',
                                   string='Feed')
    feed_lot = fields.Many2one(comodel_name='stock.lot',
                               string='Feed Lot')
    uom = fields.Many2one(comodel_name='uom.uom', string='UOM',
                          required=True)
    feed_quantity = fields.Float(string='Comsumed Cuantity', required=True,
                                 digits=(4, 2), default=1)
    start_date = fields.Date(string='Start Date',
                             default=fields.Date.today(),
                             help='Start date of the period in'
                             'which the given quantity of product was'
                             'consumed.')
    end_date = fields.Date(string='End Date', default=fields.Date.today(),
                           help='End date of the period in which the given'
                           'quantity of product was consumed. It is the date'
                           'of event\'s timestamp.')
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move')

    @api.onchange('specie')
    def onchange_specie(self):
        for res in self:
            if res.job_order:
                res.job_order.write({'specie': res.specie.id})

    @api.onchange('move')
    def onchange_move(self):
        for res in self:
            if len(res.move) > 0:
                res.feed_product = res.move.product_id
                res.uom = res.move.product_uom
                res.feed_quantity = res.move.product_qty
                res.farm = res.move.location_dest_id.location_id.location_id
                res.dest_yard = \
                    res.move.location_dest_id.locations_to_fed.location
                res.feed_location = res.move.location_id
                res.location_dest = res.move.location_dest_id
                res.start_date = res.move.picking_id.date
                party = self.env['farm.animal.group'].search(
                        [('location', '=', res.dest_yard.id),
                         ('quantity', '>', 0)])
                if party:
                    res.specie = party[0].specie
                if len(res.move.reserved_quant_ids) > 0:
                    res.feed_lot = res.move.reserved_quant_ids[0].lot_id
                else:
                    if len(res.move.quant_ids) > 0:
                        res.feed_lot = res.move.quant_ids[-1].lot_id
            print('sale')

    @api.model_create_multi
    def create(self, vals):
        res = super(GeneralFeedEventOrder, self).create(vals)
        if len(res.move) == 0:
            move_line_obj = self.env['stock.move.line']
            moves_obj = self.env['stock.move']
            new_move = moves_obj.create({
                'name': res.name+'-'+res.feed_lot.name+'-mov',
                'create_date': fields.Date.today(),
                'date': res.start_date,
                'product_id': res.feed_product.id,
                'product_uom_qty': res.feed_quantity,
                'product_uom': res.uom.id,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location_dest.id,
                'company_id': res.feed_location.company_id.id,
                'origin': res.name,
                'picked': True,
                })
            move_line_vals = {
                'move_id': new_move.id,
                'product_id': res.feed_product.id,
                'product_uom_id': res.uom.id,
                'quantity': res.feed_quantity,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location_dest.id,
                }
            if res.feed_lot:
                move_line_vals['lot_id'] = res.feed_lot.id
            new_mline = move_line_obj.create(move_line_vals)
            res.move = new_move
        else:
            new_move = res.move
        self.standard_feed(res, new_move)
        if new_move.state != 'done':
            new_mline._action_done()
        #session = ConnectorSession.from_env(self.env)
        #confirm_feed_event.delay(
        #    session, 'farm.general.feed.event', res.id)
        self.confirm_feed_event('farm.general.feed.event', res.id)
        return res

    def do_old_events(self, new_event):
        old_event = self.env['farm.general.feed.event'].search([
            ('location_dest', '=' , new_event.location_dest.id),
            ('state', '=', 'draft'), ('id', '!=', new_event.id)])
        for event in old_event:
            event.end_date = new_event.start_date
            event.confirm()

    def standard_feed(self, res, new_move):
        if res.distribution_type == 'farm':
            farm_animal_groups_obj = self.env['farm.animal.group'].search([
                ('farm', '=', res.farm.id),
                ('location.scrap_location', '!=', True),
                ('state', '!=', 'sold')])
            farm_animal_obj = self.env['farm.animal'].search([
                ('farm', '=', res.farm.id)])
        else:
            farm_animal_groups_obj = self.env['farm.animal.group'].search([
                ('location', '=', res.dest_yard.id),
                ('location.scrap_location', '!=', True),
                ('state', '!=', 'sold'), ('quantity', '>', 0)])
            farm_animal_obj = self.env['farm.animal'].search([
                ('location', '=', res.dest_yard.id)])
        farm_job_order_obj = self.env['farm.event.order']
        feed_event_obj = self.env['farm.feed.event']
        num_of_animals = 0
        for group in farm_animal_groups_obj:
            num_of_animals = num_of_animals + group.quantity
        num_of_animals = num_of_animals + len(farm_animal_obj)
        if num_of_animals == 0:
            raise Warning(_("Yard empty"))
        feed_per_animal = res.feed_quantity/num_of_animals
        new_order = farm_job_order_obj.create({
            'specie': res.specie.id,
            'event_type': 'feed',
            'farm': res.farm.id,
            'timestamp': res.timestamp,
            'employee': res.employee.id,
            })
        for group in farm_animal_groups_obj:
            feed_event_obj.create({
                'location': res.location_dest.id,
                'feed_location': res.feed_location.id,
                'feed_product': res.feed_product.id,
                'feed_lot': res.feed_lot.id,
                'uom': res.uom.id,
                'quantity': group.quantity,
                'specie': res.specie.id,
                'animal_group': group.id,
                'feed_quantity': feed_per_animal * group.quantity,
                'start_date': res.start_date,
                'end_date': res.end_date,
                'animal_type': 'group',
                'farm': res.farm.id,
                'job_order': new_order.id,
                'move': new_move.id})
        for animal in farm_animal_obj:
            feed_event_obj.create({
                'location': res.location_dest.id,
                'feed_location': res.feed_location.id,
                'feed_product': res.feed_product.id,
                'feed_lot': res.feed_lot.id,
                'uom': res.uom.id,
                'animal': animal.id,
                'farm': res.farm.id,
                'specie': res.specie.id,
                'feed_quantity': feed_per_animal,
                'start_date': res.start_date,
                'end_date': res.end_date,
                'animal_type': animal.type,
                'job_order': new_order.id,
                'move': new_move.id})
        res.job_order = new_order

    def confirm(self):
        if self.move.product_qty != self.feed_quantity:
            for event in self.job_order.feed_events:
                event.unlink()
            self.standard_feed(self, self.move)
        for event in self.job_order.feed_events:
            event.end_date = self.end_date 
        self.job_order.confirm()
        self.state = 'validated'


#@job(default_channel='root.farm_feed_validate')
def confirm_feed_event(self, model_name, order_id):
    model = self.env[model_name]
    order = model.browse(order_id)
    order.do_old_events(order)
    #session.cr.commit()
