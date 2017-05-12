# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ConsumeStock(models.Model):
    _name = 'farm.consume.stock'

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             default='draft')
    type = fields.Selection([('farm', 'Farm'), ('yard', 'Yard')],
                            string='Distribution Type')
    origin = fields.Many2one(string='Origin',
                             comodel_name='stock.location')
    to_location = fields.Many2one(string='Destinity',
                                  comodel_name='stock.location')
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product')
    lot_id = fields.Many2one(string='Lot', comodel_name='stock.production.lot')
    quantity = fields.Float(string='Quantity')
    date = fields.Date(string='Date', defaut=fields.Date.today())

    @api.multi
    @api.onchange('type')
    def onchange_type(self):
        for res in self:
            if res.type and res.type == 'farm':
                return {'domain': {'to_location': [('usage', '=', 'view')]}}
            else:
                return {'domain': {'to_location': [('usage', '!=', 'view')]}}

    @api.multi
    @api.onchange('origin')
    def onchange_location(self):
        for res in self:
            ids = []
            quants = self.env['stock.quant'].search([
                ('location_id', '=', res.origin.id),
                ('qty', '>', 0)
                ])
            for q in quants:
                ids.append(q.product_id.id)
            return {'domain': {'product_id': [('id', 'in', ids)]}}

    @api.multi
    @api.onchange('product_id')
    def onchange_product(self):
        for res in self:
            ids = []
            quants = self.env['stock.quant'].search([
                ('location_id', '=', res.origin.id),
                ('product_id', '=', res.product_id.id)])
            for q in quants:
                ids.append(q.lot_id.id)
            return {'domain': {
                        'lot_id': [('id', 'in', ids)]}}
    @api.multi
    @api.onchange('lot_id')
    def on_change_lot(self):
        for res in self:
            quants = self.env['stock.quant'].search([
                ('location_id', '=', res.origin.id),
                ('product_id', '=', res.product_id.id),
                ('lot_id', '=', res.lot_id.id)])
            total = 0
            for q in quants:
                total = total + q.qty
            res.quantity = total

    @api.multi
    def get_cost(self, lot, qty):
        cost = 0
        if lot and lot.unit_cost and lot.unit_cost > 0:
            cost = lot.unit_cost * qty
        else:
            if lot:
                quants_obj = self.env['stock.quant']
                quants = quants_obj.search([
                    ('lot_id', '=', lot.id)])
                ids = []
                for q in quants:
                    ids.append(q.id)
                moves = self.env['stock.move'].with_context({}).search([
                    ('quant_ids', 'in', ids),
                    ('picking_id', '!=', False)])
                amount = 0.0
                raw_qty = 0
                for mov in moves:
                    if mov.price_unit > 0:
                        amount += mov.price_unit * mov.product_qty
                        raw_qty = raw_qty + mov.product_qty
                if raw_qty > 0:
                    unit_price = amount/raw_qty
                    cost += qty * unit_price
                if cost == 0:
                    cost = lot.product_id.product_tmpl_id.list_price * qty
            else:
                cost = lot.product_id.product_tmpl_id.list_price * qty
        return cost

    @api.multi
    def confirm(self):
        quants_obj = self.env['stock.quant']
        for res in self:
            species = self.env['farm.specie'].search(
                [(True, '=', True)])
            remov_locs = []
            for specie in species:
                remov_locs.append(specie.removed_location.id)
            if res.type == 'farm':
                condition = ('farm', '=', res.to_location.id)
            else:
                condition = ('location', '=', res.to_location.id)
            afected_ani = self.env['farm.animal'].search([
                condition, ('location', 'not in', remov_locs)])
            afected_gro = self.env['farm.animal.group'].search([
                condition, ('state', '!=', 'sold'),
                ('location', 'not in', remov_locs)])
            afected_animals = [afected_gro, afected_ani]
            num_ani = len(afected_ani)
            for party in afected_gro:
                num_ani = num_ani + party.quantity
            cost = self.get_cost(res.lot_id, res.quantity)
            if num_ani > 0:
                cost_p_an = cost/num_ani
                for gro in afected_gro:
                    self.set_party_cost(gro, res.date, cost_p_an)
                for an in afected_ani:
                    self.set_animal_cost(an, res.date, cost_p_an)
            else:
                if res. type == 'farm':
                    farm = res.to_location
                else:
                    farm = self.get_farm(res.to_location)
                analitic_remain_ob = self.env['purchase.analitic.remain']
                analitic_remain = analitic_remain_ob.search([
                        ('farm', '=', farm.id)])
                if len(analitic_remain) == 0:
                    analitic_remain_ob.create({
                        'farm': farm.id,
                        'quantity': cost})
                else:
                    analitic_remain.quantity = analitic_remain.quantity\
                        + cost
            consumed_quants = False
            if res.lot_id:
                consumed_quants = quants_obj.search([
                        ('lot_id', '=', res.lot_id.id),
                        ('location_id', '=', res.origin.id)])
            if not consumed_quants:
                consumed_quants = quants_obj.search([
                    ('location_id', '=', res.origin.id)])
            consumed_goods = res.quantity
            for q in consumed_quants:
                if q.qty >= consumed_goods:
                    q.qty -= consumed_goods
                    consumed_goods = 0
                else:
                    consumed_goods -= q.qty
                    q.qty = 0
            res.state = 'confirmed'

    def get_farm(self, location):
        while(location.location_id.id != 1):
            location = location.location_id
        return location

    @api.multi
    def set_party_cost(self, party, date, cost_per_animal_day):
        company = self.env['res.company'].with_context({}).search([
            ('id', '=', 1)])
        journal = self.env['account.analytic.journal'].with_context(
            {}).search([('code', '=', 'PUR')])
        analytic_line_obj = self.env['account.analytic.line']
        analytic_line_obj.create({
            'name': 'consum',
            'date': date,
            'amount': -(cost_per_animal_day * party.quantity),
            'unit_amount': party.quantity,
            'account_id': party.account.id,
            'general_account_id': company.feed_account.id,
            'journal_id': journal.id,
            })

    @api.multi
    def set_animal_cost(self, animal, date, cost_per_animal_day):
        company = self.env['res.company'].with_context({}).search([
            ('id', '=', animal.farm.company_id.id)])
        journal = self.env['account.analytic.journal'].with_context(
            {}).search([('code', '=', 'PUR')])
        analytic_line_obj = self.env['account.analytic.line']
        analytic_line_obj.create({
            'name': 'consum',
            'date': date,
            'amount': -cost_per_animal_day,
            'unit_amount': 1,
            'account_id': animal.account.id,
            'general_account_id': company.feed_account.id,
            'journal_id': journal.id,
            })
            