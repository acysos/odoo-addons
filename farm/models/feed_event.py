# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from datetime import datetime


DFORMAT = "%Y-%m-%d"


class FeedEvent(models.Model):
    _name = 'farm.feed.event'
    _inherit = {'farm.event.feed_mixin': 'FeedEventMixin_id'}
    _auto = True

    animal_type = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),
        ('individual', 'Individual'), ('group', 'Group'),
        ], string="Animal Type", select=True, default='individual')
    feed_quantity_animal_day = fields.Float(string='Qty. per Animal Day',
                                            digits=(16, 4),
                                            compute='get_feed_per_day')

    @api.model_create_multi
    def create(self, vals):
        res = super(FeedEvent, self).create(vals)
        if len(res.move) == 0:
            m_line_obj = self.env['stock.move.line']
            moves_obj = self.env['stock.move']
            new_move = moves_obj.create({
                'name': res.job_order.name+'-'+res.lot.name+'-mov',
                'create_date': fields.Date.today(),
                'date': res.start_date,
                'product_id': res.feed_product.id,
                'product_uom_qty': res.feed_quantity,
                'product_uom': res.uom.id,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location.id,
                'company_id': res.location.company_id.id,
                'origin': res.job_order.name,
                'picked': True,
                })
            m_line_obj.create({
                'move_id': new_move.id,
                'product_id': res.feed_product.id,
                'product_uom_id': res.uom.id,
                'quantity': res.feed_quantity,
                'location_id': res.feed_location.id,
                'location_dest_id': res.location.id,
                'lot_id': res.feed_lot.id,
                })
            res.move = new_move
            new_move._action_done()
        return res

    def get_feed_per_day(self):
        for res in self:
            if res.animal or res.animal_group:
                if res.feed_quantity and res.start_date and res.end_date:
                    days = (res.end_date -
                            res.start_date).days
                    if days > 0:
                        res.feed_quantity_animal_day = \
                            (res.feed_quantity/res.quantity)/days

    @api.onchange('move')
    def onchange_move(self):
        for res in self:
            if len(res.move) > 0:
                res.feed_product = res.move.product_id
                res.uom = res.move.product_uom
                res.feed_quantity = res.move.product_qty
                res.farm = res.move.location_dest_id.location_id.location_id
                res.feed_location = res.move.location_id
                res.location = res.move.location_dest_id
                if len(res.move.reserved_quant_ids) > 0:
                    res.feed_lot = res.move.reserved_quant_ids[0].lot_id
                else:
                    if len(res.move.quant_ids) > 0:
                        res.feed_lot = res.move.quant_ids[-1].lot_id


    def confirm(self):
        for res in self:
            quants_obj = self.env['stock.quant']
            if res.animal_type == 'group':
                res.animal_group.feed_quantity += res.feed_quantity

            else:
                res.animal.consumed_feed += res.feed_quantity
            res.consume_feed('consume_feed', res.end_date, res.feed_product,
                              res.feed_lot, res.specie, res.location,
                              res.feed_quantity, res.uom)
            return super(FeedEvent, res).confirm()

