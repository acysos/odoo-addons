# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning

EVENT_STATES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ]
DISTRIBUTION_TYPES = [
    ('farm', 'Farm'), ('yard', 'Yard')]


class general_medicaton_event(models.Model):
    _name = 'farm.general.medication.event'

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
                                         default='farm')
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
    medication_in_feed = fields.Boolean(string='Medication in feed')
    medicated_feed = fields.Many2one(comodel_name='product.product',
                                     string='Medicated feed')
    feed_location = fields.Many2one(comodel_name='stock.location',
                                    string='Medication Source', required=True)
    feed_product = fields.Many2one(comodel_name='product.product',
                                   string='medication')
    feed_lot = fields.Many2one(comodel_name='stock.production.lot',
                               string='Medication Lot')
    uom = fields.Many2one(comodel_name='product.uom', string='UOM',
                          required=True)
    feed_quantity = fields.Float(string='Comsumed Cuantity', required=True,
                                 digits=(4, 2), default=1)
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move')
    prescription = fields.Many2one(comodel_name='farm.prescription',
                                   string='Prscription')

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(general_medicaton_event, self).create(vals)
        if len(res.move) == 0:
            quants_obj = self.env['stock.quant']
            moves_obj = self.env['stock.move']
            target_quant = quants_obj.search([
                ('lot_id', '=', res.feed_lot.id),
                ('location_id', '=', res.feed_location.id)])
            new_move = moves_obj.create({
                'name': res.name+'-'+res.feed_lot.name+'-mov',
                'create_date': fields.Date.today(),
                'product_id': res.feed_product.id,
                'product_uom_qty': res.feed_quantity,
                'product_uom': res.uom.id,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location_dest.id,
                'company_id': res.feed_location.company_id.id,
                'origin': res.name,
                })
            for q in target_quant:
                q.reservation_id = new_move.id
            res.move = new_move
        else:
            new_move = res.move
        if res.distribution_type == 'farm':
            farm_animal_groups_obj = self.env['farm.animal.group'].search([
                ('farm', '=', res.farm.id),
                ('state', '!=', 'sold')])
            farm_animal_obj = self.env['farm.animal'].search([
                ('farm', '=', res.farm.id)])
        else:
            farm_animal_groups_obj = self.env['farm.animal.group'].search([
                ('location', '=', res.dest_yard.id),
                ('state', '!=', 'sold')])
            farm_animal_obj = self.env['farm.animal'].search([
                ('location', '=', res.dest_yard.id)])
        farm_job_order_obj = self.env['farm.event.order']
        medication_event_obj = self.env['farm.medication.event']
        num_of_animals = 0
        for group in farm_animal_groups_obj:
            num_of_animals += group.quantity
        num_of_animals = num_of_animals + len(farm_animal_obj)
        feed_per_animal = res.feed_quantity/num_of_animals
        new_order = farm_job_order_obj.create({
            'specie': res.specie.id,
            'event_type': 'medication',
            'farm': res.farm.id,
            'timestamp': res.timestamp,
            'employee': res.employee.id,
            })
        pre_group_obj = self.env['farm.prescription.animal_group']
        pre_ani_obj = self.env['farm.prescription.animal']
        for group in farm_animal_groups_obj:
            pre_group_obj.create({
                'prescription': res.prescription.id,
                'party': group.id})
            medication_event_obj.create({
                'location': res.location_dest.id,
                'feed_location': res.feed_location.id,
                'feed_product': res.feed_product.id,
                'uom': res.feed_product.product_tmpl_id.uom_id.id,
                'feed_lot': res.feed_lot.id,
                'specie': res.specie.id,
                'medicated_feed': res.medicated_feed.id,
                'medication_in_feed': res.medication_in_feed,
                'animal_group': group.id,
                'feed_quantity': feed_per_animal * group.quantity,
                'animal_type': 'group',
                'farm': res.farm.id,
                'job_order': new_order.id,
                'prescription': res.prescription.id,
                'move': new_move.id})
        for animal in farm_animal_obj:
            pre_ani_obj.create({
                'prescription': res.prescription.id,
                'animal': animal.id})
            medication_event_obj.create({
                'location': res.location_dest.id,
                'feed_location': res.feed_location.id,
                'feed_product': res.feed_product.id,
                'feed_lot': res.feed_lot.id,
                'medicated_feed': res.medicated_feed.id,
                'feed_product_uom_category': res.uom.id,
                'uom': res.feed_product.uom_id.id,
                'animal': animal.id,
                'farm': res.farm.id,
                'medication_in_feed': res.medication_in_feed,
                'specie': res.specie.id,
                'feed_quantity': feed_per_animal,
                'animal_type': animal.type,
                'job_order': new_order.id,
                'prescription': res.prescription.id,
                'move': new_move.id})
        res.job_order = new_order
        return res

    @api.multi
    def form_validations(self):
        for res in self:
            if res.farm != res.prescription.farm:
                raise Warning(
                    _("farms are diferen in event and prescription"))
    
    @api.multi
    def confirm(self):
        for res in self:
            res.job_order.confirm()
            res.state = 'validated'
