# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
from openerp.exceptions import Warning


class analitic_account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        for res in self:
            if res.type == 'out_invoice' or res.type == 'out_refund':
                if res.type == 'out_invoice':
                    ref_id = res.id
                    line_name = 'sale'
                else:
                    ref_id = res.origin_invoices_ids[0].id
                    line_name = 'refund'
                self.create_analitic_move(ref_id, res, line_name)
        return super(analitic_account_invoice, self).invoice_validate()

    @api.multi
    @api.returns('self')
    def refund(self, date=None, period_id=None, description=None,
               journal_id=None):
        for res in self:
            if res.type == 'out_invoice':
                ref_id = res.id
                line_name = 'invoice-cancel'
                self.create_analitic_move(ref_id, res, line_name)
        return super(
            analitic_account_invoice, self).refund(date, period_id,
                                                   description, journal_id)

    def create_analitic_move(self, ref_id, res, line_name):
        analytic_line_obj = self.env['account.analytic.line']
        sales = self.env['sale.order'].search([
            ('invoice_ids', 'in', [ref_id, ])])
        animal_total = 0
        sale_animal = []
        for sale in sales:
            for sline in sale.order_line:
                procurement = self.env['procurement.order'].search([
                    ('sale_line_id', '=', sline.id)])
                moves = self.env['stock.move'].search([
                    ('procurement_id', '=', procurement.id)])
                lots = []
                for move in moves:
                    for lot in move.quant_ids:
                        operations = self.env['stock.pack.operation'].search([
                            ('picking_id', '=', move.picking_id.id),
                            ('lot_id', '=', lot.lot_id.id)])
                        for op in operations:
                            lots.append([lot.lot_id.name, op.product_qty])
                animals_obj = self.env['farm.animal.group']
                partys = animals_obj.search([(True, '=', True)])
                for party in partys:
                    for lot in lots:
                        if party.number == lot[0]:
                            sale_animal.append([party, lot[1]])
                            animal_total = animal_total + lot[1]
        if len(sale_animal) > 0:
            total_price = 0
            for line in res.invoice_line:
                total_price = total_price \
                    + line.price_subtotal
            if line_name == 'invoice-cancel':
                total_price = total_price * -1
            price_unit = total_price/animal_total
            for group in sale_animal:
                company = self.env['res.company'].search([
                    (True, '=', True)])[0]
                journal = self.env[
                    'account.analytic.journal'].search([
                        ('code', '=', 'FAR')])
                amount = price_unit * group[1]
                analytic_line_obj.create({
                    'name': line_name,
                    'date': res.date_invoice,
                    'amount': amount,
                    'unit_amount': group[1],
                    'account_id': group[0].account.id,
                    'general_account_id': company.feed_account.id,
                    'journal_id': journal.id,
                    })
        else:
            species_obj = self.env['farm.specie']
            for specie in species_obj:
                if move.product_id.id == specie.group_product.id:
                    raise Warning(_('group sold not found'))
