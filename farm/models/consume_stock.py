# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ConsumeStock(models.Model):
    _name = 'farm.consume.stock'

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             default='draft')
    type = fields.Selection([('farm', 'Farm'), ('yard', 'Yard')],
                            string='Distribution Type', default='farm')
    origin = fields.Many2one(string='Origin',
                             comodel_name='stock.location')
    to_location = fields.Many2one(string='Destinity',
                                  comodel_name='stock.location')
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product')
    lot_id = fields.Many2one(string='Lot', comodel_name='stock.lot')
    quantity = fields.Float(string='Quantity')
    date = fields.Date(string='Date', defaut=fields.Date.today())
    allowed_products = fields.Many2many(comodel_name='product.product',
                                        string='Allowed Products', compute='_get_allowed_products')
    allowed_lots = fields.Many2many(comodel_name='stock.lot',
                                    string='Allowed Lots', compute='_get_allowed_lots')
    allowed_locations = fields.Many2many(comodel_name='stock.location',
                                         string='Allowed Locations', compute='_get_allowed_locations')


    @api.depends('type')
    def _get_allowed_locations(self):
        for res in self:
            loc_obj = self.env['stock.location']
            if res.type and res.type == 'farm':
                res.allowed_locations = [(6, 0, loc_obj.search([('usage', '=', 'view')]).ids)]
            else:
                res.allowed_locations = [(6, 0, loc_obj.search([('usage', '!=', 'view')]).ids)]

    @api.depends('origin')
    def _get_allowed_products(self):
        for res in self:
            ids = []
            if res.origin:
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', res.origin.id),
                    ('quantity', '>', 0)
                    ])
                for q in quants:
                    ids.append(q.product_id.id)
            res.allowed_products = [(6, 0, ids)]

    @api.depends('product_id')
    def _get_allowed_lots(self):
        for res in self:
            ids = []
            if res.product_id and res.origin:
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', res.origin.id),
                    ('product_id', '=', res.product_id.id)])
                for q in quants:
                    ids.append(q.lot_id.id)
            res.allowed_lots = [(6, 0, ids)]

    @api.onchange('lot_id')
    def on_change_lot(self):
        for res in self:
            if res.lot_id and res.product_id and res.origin:
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', res.origin.id),
                    ('product_id', '=', res.product_id.id),
                    ('lot_id', '=', res.lot_id.id)])
                total = 0
                for q in quants:
                    total = total + q.quantity
                res.quantity = total
            else:
                res.quantity = 0

    def confirm(self):
        moves_obj = self.env['stock.move']
        m_line_obj = self.env['stock.move.line']
        scrap = self.env['stock.location'].search(
            [('scrap_location', '=', True)])[0]
        for res in self:
            new_move = moves_obj.create({
                'name': 'consume',
                'create_date': fields.Date.today(),
                'date': res.date,
                'product_id': res.product_id.id,
                'product_uom_qty': res.quantity,
                'product_uom': res.product_id.product_tmpl_id.uom_id.id,
                'location_id': res.origin.id,
                'location_dest_id': scrap.id,
                'company_id': res.origin.company_id.id,
                'picked': True,
                })
            m_line_vals = {
                'move_id': new_move.id,
                'product_id': res.product_id.id,
                'product_uom_id': res.product_id.product_tmpl_id.uom_id.id,
                'quantity': res.quantity,
                'location_id': res.origin.id,
                'location_dest_id': scrap.id,
            }
            if res.lot_id:
                m_line_vals['lot_id'] = res.lot_id.id
            m_line_obj.create(m_line_vals)
            new_move._action_done()
            res.state = 'confirmed'

    def get_farm(self, location):
        while(location.location_id.id != 1):
            location = location.location_id
        return location
