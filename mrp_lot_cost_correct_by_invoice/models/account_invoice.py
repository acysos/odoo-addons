# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for res in self:
            if res.type == 'in_invoice':
                control = False
                for line in res.invoice_line:
                    if line.product_id.product_tmpl_id.categ_id.raw_material:
                        control = True
                        cur_line = line
                if control:
                    self.correct_lot_cost(res, cur_line)
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def correct_lot_cost(self, res, cur_line):
        line_ids = []
        for inv_line in res.invoice_line:
            if inv_line.purchase_line_id and \
                    inv_line.purchase_line_id.id not in line_ids:
                line_ids.append(inv_line.purchase_line_id.id)
        if len(line_ids) == 1:
            purchase = self.env['purchase.order'].search(
                [('order_line', 'in', line_ids)])
            if purchase.order_line[0].price_unit != \
                    cur_line.price_unit or \
                    len(res.invoice_line) > 1:
                self.calc_correction(res.amount_untaxed, purchase, cur_line)

    @api.multi
    def calc_correction(self, amount_tot, purchase, cur_line):
        product = purchase.order_line[0].product_id
        total_qty = purchase.order_line[0].product_qty
        line_qty = cur_line.quantity
        amount_pu = amount_tot/line_qty
        absolut_dif_pu = amount_pu - purchase.order_line[0].price_unit
        rel_dif_pu = absolut_dif_pu * (line_qty/total_qty)
        pickings = self.env['stock.picking'].search(
            [('origin', '=', purchase.name), ('state', '=', 'done')])
        product_lot = pickings[0].move_lines[0].quant_ids[0].lot_id
        new_price = purchase.order_line[0].price_unit + rel_dif_pu
        self.do_correction(product, rel_dif_pu, new_price, product_lot)

    @api.multi
    def do_correction(self, product, dif_pu, new_price, lot):
        stock_quant_obj = self.env['stock.quant']
        stock_move_obj = self.env['stock.move']
        lot.unit_cost = new_price
        quants = stock_quant_obj.search([
                    ('product_id', '=', product.id,),
                    ('lot_id', '=', lot.id)])
        ids = []
        for q in quants:
            ids.append(q.id)
        moves = stock_move_obj.search([
                    ('quant_ids', 'in', ids),
                    ('raw_material_production_id', '!=', False)])
        for mov in moves:
            out_total = mov.raw_material_production_id.product_qty
            if out_total > 1:
                lot_dif = (mov.product_qty/out_total) * dif_pu
                self.correct_lot_unit_cost(
                    lot_dif, mov.raw_material_production_id)

    @api.multi
    def correct_lot_unit_cost(self, dif, production):
        moves = self.env['stock.move'].search(
            [('production_id', '=', production.id)])
        for mov in moves:
            if mov.product_qty > 1:
                for q in mov.quant_ids:
                    lot = q.lot_id
                    lot.unit_cost = lot.unit_cost + dif
