# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class InseminationEvent(models.Model):
    _name = 'farm.insemination.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}
    _rec_name = 'animal'
    _auto = True

    dose_bom = fields.Many2one(comodel_name='mrp.bom', string='Dose',
                               domain=[(('semen_dose', '=', True))])
    dose_product = fields.Many2one(comodel_name='product.product',
                                   string='Dose product', required=True)
    dose_lot = fields.Many2one(comodel_name='stock.production.lot',
                               string='Dose lot')
    female_cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                                   string='Female cycle')
    move = fields.Many2one(comodel_name='stock.move', string='Stock move',
                           readonly=True)

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise Warning(
                _("Only females can be bred"))
        current_cycle = self.animal.current_cycle
        if (not current_cycle or current_cycle.diagnosis_events or
                current_cycle.farrowing_event):
            self.create_new_female_cycle()
        elif not self.female_cycle:
            self.female_cycle = self.animal.current_cycle
        if not self.is_ready():
            raise Warning(
                _("female's cycle is not compatible to be bred"))
        self.get_event_move()
        self.animal.update_state()
        self.female_cycle.update_state(self)
        tags_obj = self.env['farm.tags']
        tag = tags_obj.search([
            ('name', '=', self.farm.name +'-unmated')])
        tag.animal = [(3, self.animal.id)]
        new_tag = tags_obj.search([
            ('name', '=', self.farm.name + '-mated')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': self.farm.name + '-mated',
                                       })
        self.animal.tags = [(6, 0, [new_tag.id, ])]
        super(InseminationEvent, self).confirm()

    @api.onchange('dose_bom')
    def onchange_specie(self):
        product_obj = self.env['product.product']
        dose_pro = product_obj.search(
            [('product_tmpl_id', '=', self.dose_bom.product_tmpl_id.id)])
        product_ids = []
        for product in dose_pro:
            product_ids.append(product.id)
        return {'domain': {
                'dose_product': [('id', 'in', product_ids)]}}

    @api.one
    def get_event_move(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        target_quant = quants_obj.search([
            ('product_id', '=', self.dose_product.id),
            ('lot_id', '=', self.dose_lot.id),
            ('qty', '>', 1),
            ])
        if not target_quant:
            raise Warning(
                _('semen dose no avairable'))
        new_move = moves_obj.create({
            'name': 'ins' + self.dose_lot.name,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': self.dose_product.id,
            'product_uom_qty': 1,
            'product_uom': self.dose_product.uom_id.id,
            'location_id': target_quant[0].location_id.id,
            'location_dest_id': self.animal.initial_location.id,
            'company_id': self.animal.initial_location.company_id.id,
            'origin:': self.job_order.name,
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        self.move = new_move
        consumed_quants = quants_obj.search([
            ('lot_id', '=', self.dose_lot.id),
            ('location_id', '=', self.animal.initial_location.id)])
        consumed_q = 1
        for q in consumed_quants:
            if q.qty >= consumed_q:
                q.qty -= consumed_q
                consumed_q = 0
                if q.qty == 0:
                    q.unlink()
            else:
                q.qty = 0
                consumed_q -= q.qty
                q.unlink()

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.female_cycle.state == 'unmated':
            return True
        elif self.female_cycle.state == 'mated':
            return True
        else:
            return False

    @api.one
    def create_new_female_cycle(self):
        female_clicle_obj = self.env['farm.animal.female_cycle']
        self.female_cycle = female_clicle_obj.create(
            {'animal': self.animal.id, })
