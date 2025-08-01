# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2025  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning

EVENT_STATES = [
    ('draft', 'Draft'),
    ('progress', 'In progress'),
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
    feed_lot = fields.Many2one(comodel_name='stock.lot',
                               string='Medication Lot')
    uom = fields.Many2one(comodel_name='uom.uom', string='UOM',
                          required=True)
    feed_quantity = fields.Float(string='Comsumed Cuantity', required=True,
                                 digits=(4, 2), default=1)
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move')
    prescription = fields.Many2one(comodel_name='farm.prescription',
                                   string='Prscription')
    only_mated = fields.Boolean(string='Only Mated', default=False)
    provider = fields.Many2one(string='Provider',
                               comodel_name='res.partner')
    veterinarian_id = fields.Many2one(string="Veterinarian",
                                      comodel_name='farm.veterinarian')
    allowed_lots = fields.Many2many(comodel_name='stock.lot',
                                    string='Allowed Lots', compute='_get_allowed_lots')
    allowed_locations = fields.Many2many(comodel_name='stock.location',
                                         string='Allowed Locations', compute='_get_allowed_locations')


    @api.model_create_multi
    def create(self, vals):
        res = super(general_medicaton_event, self).create(vals)
        if len(res.move) == 0:
            picking_obj = self.env['stock.picking']
            warehouse = self.env['stock.warehouse'].search([
                ('view_location_id', '=', res.farm.id)])
            picking_t = self.env['stock.picking.type'].search([
                ('warehouse_id', '=', warehouse.id)])[1]
            new_pick = picking_obj.create({
                'company_id': 1,
                'partner_id': 1,
                'picking_type_id': picking_t.id,
                'move_type': 'one',
                'date_done': res.timestamp,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location_dest.id,
                })
            m_line_obj = self.env['stock.move.line']
            moves_obj = self.env['stock.move']
            new_move = moves_obj.create({
                'name': res.name+'-'+res.feed_lot.name+'-mov',
                'create_date': fields.Date.today(),
                'product_id': res.feed_product.id,
                'product_uom_qty': res.feed_quantity,
                'product_uom': res.uom.id,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location_dest.id,
                'company_id': res.feed_location.company_id.id,
                'picking_id': new_pick.id,
                'origin': res.name,
                'picked': True,
                })
            m_line_vals = {
                'move_id': new_move.id,
                'product_id': res.feed_product.id,
                'product_uom_id': res.feed_product.product_tmpl_id.uom_id.id,
                'qty_done': res.feed_quantity,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location_dest.id,
                }
            if res.feed_lot:
                m_line_vals['lot_id'] = res.feed_lot.id
            m_line_obj.create(m_line_vals)
            new_move._action_done()
            res.move = new_move
        else:
            new_move = res.move
        if not res.medication_in_feed:
            group_condition = ('state', '!=', 'sold')
            anim_condition = ('farm', '=', res.farm.id)
        elif res.medicated_feed.product_tmpl_id.feed_lactating:
            group_condition = ('state', '!=', 'sold')
            anim_condition = False
        elif res.medicated_feed.product_tmpl_id.feed_transit:
            group_condition = ('state', '!=', 'sold')
            anim_condition = False
        else:
            group_condition = ('state',  '!=', 'sold')
            anim_condition = ('farm', '=', res.farm.id)
        if res.distribution_type == 'farm':
            farm_animal_groups_obj = self.env['farm.animal.group'].search([
                ('farm', '=', res.farm.id),
                group_condition])
            farm_animal_obj = self.env['farm.animal'].search([
                anim_condition])
        else:
            farm_animal_groups_obj = self.env['farm.animal.group'].search([
                ('location', '=', res.dest_yard.id),
                group_condition])
            if res.only_mated:
                farm_animal_obj = self.env['farm.animal'].search([
                    ('location', '=', res.dest_yard.id),
                    ('state', '=', 'mated')])
            else:
                if anim_condition:
                    farm_animal_obj = self.env['farm.animal'].search([
                        ('location', '=', res.dest_yard.id),
                        anim_condition])
                else:
                    farm_animal_obj = []
        farm_job_order_obj = self.env['farm.event.order']
        medication_event_obj = self.env['farm.medication.event']
        num_of_animals = 0
        for group in farm_animal_groups_obj:
            num_of_animals += group.quantity
        num_of_animals = num_of_animals + len(farm_animal_obj)
        if num_of_animals == 0:
            raise Warning(_("yard empty or bad configuratyon of feed"))
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
        if len(res.prescription) == 0:
            pre_template = self.env['farm.prescription.template'].search([
                ('product', '=', res.feed_product.id)])
            if not pre_template:
                raise Warning(_('No found prescription template'))
            pres_vals = self.get_prescription_vals(res, pre_template)
            res.prescription = self.env['farm.prescription'].create(pres_vals)
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

    def get_prescription_vals(self, event, pre_template):
        pres_vals = {
                'veterinarian': event.veterinarian_id.id,
                'farm': event.farm.id,
                'template': pre_template.id,
                'waiting_period': pre_template.waiting_period,
                'dosage': pre_template.dosage,
                'expiry_period': pre_template.expiry_period,
                'specie': pre_template.specie.id,
                'quantity': event.feed_quantity,
                'unit': pre_template.unit.id,
                'product': pre_template.product.id,
                'afection': pre_template.afection,
                'note': pre_template.note,
                'lot': event.feed_lot.id
                }
        return pres_vals

    def form_validations(self):
        for res in self:
            if res.farm != res.prescription.farm:
                raise Warning(
                    _("farms are diferen in event and prescription"))

    @api.depends('feed_product', 'feed_lot')
    def get_provider(self):
        stock_move_obj = self.env['stock.move']
        stock_move_line = self.env['stock.move.line']
        for res in self:
            if res.feed_product and res.feed_lot:
                stoc_m_l = stock_move_line.search([
                    ('product_id', '=', res.feed_product.id,),
                    ('lot_id', '=', res.feed_lot.id)])
                moves = stock_move_obj.search([
                    ('move_line_ids', 'in', stoc_m_l.ids),
                    ('picking_id','!=', False)])
                if moves:
                    res.provider = moves[0].picking_id.partner_id

    def confirm(self):
        for res in self:
            res.job_order.confirm()
            res.prescription.confirm()
            res.state = 'validated'

    def long_confirm(self):
        for res in self:
            res.state = 'progress'
            #session = ConnectorSession.from_env(self.env)
            #confirm_medication.delay(
            #    session, 'farm.general.medication.event', res.id)
            self.confirm_medication('farm.general.medication.event', res.id)

    @api.depends('feed_product')
    def _get_allowed_locations(self):
        for res in self:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', res.feed_product.id),
                ('quantity', '>', 0)])
            ids = []
            for q in quants:
                if q.location_id.id not in ids:
                    ids.append(q.location_id.id)
            res.allowed_locations = [(6, 0, ids)]

    @api.depends('feed_product', 'feed_location')
    def _get_allowed_lots(self):
        for res in self:
            ids = []
            print('entrando a get_allowed_lots')
            if res.feed_location and res.feed_product:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', res.feed_product.id),
                    ('location_id', '=', res.feed_location.id),
                    ('quantity', '>', 0)])
                for q in quants:
                    if q.lot_id:
                        ids.append(q.lot_id.id)
            if ids:
                print('ids', ids)
                res.allowed_lots = [(6, 0, ids)]
            else:
                print('no ids')
                res.allowed_lots = [(6, 0, [])]



def confirm_medication(self, model_name, order_id):
    model = self.env[model_name]
    order = model.browse(order_id)
    order.confirm()
