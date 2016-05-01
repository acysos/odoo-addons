# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import math


class SemenExtractionEvent(models.Model):
    _name = 'farm.semen_extraction.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}
    _auto = True

    semen_product = fields.Many2one(comodel_name='product.product',
                                    string="Semen's Product")
    untreated_semen_qty = fields.Float(string='Semen Extracted Qty',
                                       required=True, digits=(16, 3))
    formula_result = fields.Float(string='Formula Result', required=True)
    solvent_calculated_qty = fields.Float(string='Calc. semen solvent Qty',
                                          compute='get_solvent_qty')
    semen_calculated_qty = fields.Float(string='Calc. Semen Produced Qty',
                                        compute='get_semen_calculated_qty')
    semen_qty = fields.Float(string='Semen Producec Quantity', digits=(16, 3))
    semen_lot = fields.Many2one(comodel_name='stock.production.lot',
                                string='Semen lot')
    semen_move = fields.Many2one(comodel_name='stock.move', string='Move')
    dose_location = fields.Many2one(comodel_name='stock.location',
                                    string='Doses Location',
                                    domain=[('usage', '=', 'internal')],
                                    required=True)
    dose_bom = fields.Many2one(comodel_name='mrp.bom',
                               string='Dose Container',
                               )
    dose_calculated_units = fields.Float(
        string='Calculated Doses',
        help='Calculates the number of doses based on Container (BoM) and '
        'Semen Produced Qty. The quantity is expressed in the UoM of the '
        'Container.\n'
        'You have to save the event to see this calculated value.',
        compute='on_change_with_dose_calculated_units')
    doses = fields.One2many(comodel_name='farm.semen_extraction.dose',
                            inverse_name='event', string='Doses')
    doses_semen_qty = fields.Float(string='Dose Semen Qty',
                                   compute='on_change_with_doses_semen_qty')
    semen_remaining_qty = fields.Float(
        string='Remaining Semen',
        compute='on_change_with_semen_remaining_qty')

    @api.onchange('specie')
    def onchange_specie(self):
        return {'domain': {
                'semen_product': [('id', '=', self.specie.semen_product.id)]}}

    @api.one
    def get_solvent_qty(self):
        self.solvent_calculated_qty = \
            self.semen_calculated_qty - self.untreated_semen_qty

    @api.one
    def get_semen_calculated_qty(self):
        self.semen_calculated_qty = \
            self.untreated_semen_qty * self.formula_result

    @api.one
    def on_change_with_dose_calculated_units(self):
        if not self.dose_bom or not self.semen_qty:
            self.dose_calculated_units = 0.0
        else:
            consumed_semen_qty = 0.0
            for line in self.dose_bom.bom_line_ids:
                if line.product_id == self.specie.semen_product:
                    consumed_semen_qty = line.product_qty
            if consumed_semen_qty == 0:
                self.dose_calculated_units = 0.0
            else:
                self.dose_calculated_units = \
                    float(self.semen_qty)/consumed_semen_qty

    @api.one
    def on_change_with_semen_remaining_qty(self):
        semen_remaining_qty = self.semen_qty or 0
        if self.semen_qty is None or not self.doses:
            self.semen_remaining_qty = semen_remaining_qty
        else:
            for dose in self.doses:
                semen_remaining_qty -= dose.semen_qty or 0.0
            self.semen_remaining_qty = semen_remaining_qty

    @api.one
    def on_change_with_doses_semen_qty(self):
        if self.semen_qty is None or not self.doses:
            self.doses_semen_qty = 0.0
        else:
            doses_qty = 0.0
            for dose in self.doses:
                doses_qty += dose.semen_qty or 0.0
            self.doses_semen_qty = doses_qty

    def is_valid(self):
        for extraction_event in self:
            extraction_event.check_doses_semen_quantity()
            extraction_event.check_deliveries_dose_quantity()

    def check_doses_semen_quantity(self):
        if self.semen_remaining_qty < 0.0:
            raise Warning(
                _('More semen in doses than produced'))

    @api.one
    def calculate_doses(self):
        Dose_obj = self.env['farm.semen_extraction.dose']
        for extraction_event in self:
            if extraction_event.doses:
                raise Warning(
                    _('dose already defined'))
            if not extraction_event.dose_bom:
                continue
            n_doses = math.floor(extraction_event.dose_calculated_units)
            Dose_obj.create({
                'event': extraction_event.id,
                'sequence': 1,
                'bom': extraction_event.dose_bom.id,
                'quantity': n_doses})

    @api.one
    def confirm(self):
        self.check_doses_semen_quantity()
        for extraction_event in self:
            if not extraction_event.doses:
                raise Warning(
                    _('no doses'))
            self.get_semen_move()
            for dose in extraction_event.doses:
                dose.get_production()
                dose.state = 'validated'
        super(SemenExtractionEvent, extraction_event).confirm()

    @api.one
    def get_semen_move(self):
        move_obj = self.env['stock.move']
        lot_obj = self.env['stock.production.lot']
        new_lot = lot_obj.create({
            'product_id': self.specie.semen_product.id})
        production_location = self.env['stock.location'].search(
            [('usage', '=', 'production')])
        new_move = move_obj.create({
            'name': 'extrac' + new_lot.name,
            'product_id': self.specie.semen_product.id,
            'product_uom_qty': self.semen_qty,
            'location_id': production_location.id,
            'location_dest_id': self.dose_location.id,
            'date': self.timestamp,
            'company_id': self.farm.company_id.id,
            'origin': 'extraction' + self.lot.name,
            'product_uom':
                self.specie.semen_product.product_tmpl_id.uom_id.id,
            })
        new_move.action_done()
        for q in new_move.quant_ids:
            q.lot_id = new_lot.id
        self.semen_move = new_move
        self.semen_lot = new_lot


class SemenExtractionDose(models.Model):
    _name = 'farm.semen_extraction.dose'
    _order = 'sequence ASC'

    event = fields.Many2one(comodel_name='farm.semen_extraction.event',
                            string='Event')
    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             compute='get_specie')
    state = fields.Selection(string='state',
                             selection=[
                                    ('draft', 'Draft'),
                                    ('validated', 'Validated')],
                             default='draft')
    sequence = fields.Integer(string='Line Num', required=True)
    bom = fields.Many2one(comodel_name='mrp.bom', string='Container',
                          required=True,
                          domain=[('semen_dose', '=', True), ])
    quantity = fields.Integer(string='Quantity', required=True)
    semen_qty = fields.Float(string='Semen Qty', compute='get_qty')
    dose_product = fields.Many2one(comodel_name='product.product',
                                   string="Dose Product")
    production = fields.Many2one(comodel_name='mrp.production',
                                 string='production')
    lot = fields.Many2one(comodel_name='stock.production.lot',
                          string='Lot')

    @api.one
    def get_qty(self):
        if not self.event or not self.bom or not self.quantity:
            self.semen_qty = False
        else:
            semen_product = self.event.specie.semen_product
            semen_qty = 0.0
            for line in self.bom.bom_line_ids:
                if line.product_id == semen_product:
                    semen_qty = line.product_qty*self.quantity
                    break
            self.semen_qty = semen_qty

    @api.one
    def get_specie(self):
        self.specie = self.event.specie

    @api.one
    def get_production(self):
        production_location = self.env['stock.location'].search(
            [('usage', '=', 'production')])
        production_obj = self.env['mrp.production']
        products_obj = self.env['product.product']
        produce_line_obj = self.env['mrp.product.produce.line']
        wiz_product_produce_obj = self.env['mrp.product.produce']
        manu_product = products_obj.search(
            [('product_tmpl_id', '=', self.bom.product_tmpl_id.id)])
        new_production = production_obj.create({
            'name': self.event,
            'date_planned': self.event.timestamp,
            'company_id': self.event.farm.company_id.id,
            'product_id': manu_product.id,
            'bom_id': self.bom.id,
            'product_uom': self.bom.product_tmpl_id.uom_id.id,
            'location_src_id': self.event.dose_location.id,
            'location_dest_id': self.event.dose_location.id,
            'product_qty': self.quantity,
            'origin': self.event.job_order.name
            })
        new_production.action_confirm()
        new_production.action_ready()
        '''
        for line in new_production.move_lines:
            line.location_id = production_location
        '''
        lots_obj = self.env['stock.production.lot']
        new_lot = lots_obj.create({
            'product_id': manu_product.id, })
        new_wiz_production = wiz_product_produce_obj.create({
            'product_id': manu_product.id,
            'product_qty': self.quantity,
            'mode': 'consume_produce',
            'lot_id': new_lot.id,
            })
        for line in new_production.move_lines:
            produce_line_obj.create({
                'product_id': line.product_id.id,
                'product_qty': line.product_uom_qty,
                'lot_id': self.event.semen_lot.id,
                'produce_id': new_wiz_production.id,
                })
        new_production.action_produce(self.quantity,
            'consume_produce', new_wiz_production)
        new_production.action_production_end()
        self.production = new_production
        self.lot = new_lot
