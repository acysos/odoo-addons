# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning


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

    def confirm(self):
        for res in self:
            if not res.is_compatible():
                raise Warning(
                    _("Only females can be bred"))
            current_cycle = res.animal.current_cycle
            if (not current_cycle or current_cycle.diagnosis_events or
                    current_cycle.farrowing_event):
                res.create_new_female_cycle()
            elif not res.female_cycle:
                res.female_cycle = res.animal.current_cycle
            if not res.is_ready():
                raise Warning(
                    _("female's cycle is not compatible to be bred"))
            res.get_event_move()
            res.animal.update_state()
            res.female_cycle.update_state(res)
            tags_obj = self.env['farm.tags']
            tag = tags_obj.search([
                ('name', '=', res.farm.name +'-unmated')])
            tag.animal = [(3, res.animal.id)]
            new_tag = tags_obj.search([
                ('name', '=', res.farm.name + '-mated')])
            if len(new_tag) == 0:
                new_tag = tags_obj.create({'name': res.farm.name + '-mated',
                                           })
            res.animal.tags = [(6, 0, [new_tag.id, ])]
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

    def get_event_move(self):
        for res in self:
            moves_obj = self.env['stock.move']
            quants_obj = self.env['stock.quant']
            target_quant = quants_obj.search([
                ('product_id', '=', res.dose_product.id),
                ('lot_id', '=', res.dose_lot.id),
                ('qty', '>', 1),
                ])
            if not target_quant:
                raise Warning(
                    _('semen dose no avairable'))
            new_move = moves_obj.create({
                'name': 'ins' + res.dose_lot.name,
                'create_date': fields.Date.today(),
                'date': res.timestamp,
                'product_id': res.dose_product.id,
                'product_uom_qty': 1,
                'product_uom': res.dose_product.uom_id.id,
                'location_id': target_quant[0].location_id.id,
                'location_dest_id': res.specie.consumed_feed_location.id,
                'company_id': res.animal.initial_location.company_id.id,
                'origin': res.job_order.name,
                })
            for q in target_quant:
                q.reservation_id = new_move.id
            new_move.action_done()
            res.move = new_move

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

    def create_new_female_cycle(self):
        for res in self:
            female_clicle_obj = self.env['farm.animal.female_cycle']
            res.female_cycle = female_clicle_obj.create(
                {'animal': res.animal.id, })
