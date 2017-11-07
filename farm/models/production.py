# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime, timedelta
from mx.DateTime.DateTime import today

DFORMAT = "%Y-%m-%d %H:%M:%S"


class BOM(models.Model):
    _inherit = 'mrp.bom'

    semen_dose = fields.Boolean(string='Semen Dose')
    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Dose Specie')

class MrpAnaliticRemain(models.Model):
    _name= 'mrp.analitic.remain'

    date = fields.Date(string='Date')
    qty_per_unit = fields.Float(string='Cost per unit')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    '''
    @api.multi
    def calculateCost(self, wiz):
        super(MrpProduction, self).calculateCost(wiz)
        analitic_remain_ob = self.env['purchase.analitic.remain']
        remain_history = self.env['mrp.analitic.remain']
        factory = self.env['stock.location'].search([
            ('factory', '=', True)])
        analitic_remain = analitic_remain_ob.search([
                                    ('farm', '=', factory.id)])
        if len(analitic_remain) > 0 and analitic_remain.quantity > 0:
            today = datetime.today()
            if analitic_remain.last_calc:
                last_calc = datetime.strptime(
                    analitic_remain.last_calc, DFORMAT)
                dif = today - last_calc
            else:
                dif = 3
            if dif > 1:
                self.get_last_productions(analitic_remain, today)
            wiz.lot_id.unit_cost = wiz.lot_id.unit_cost \
                + analitic_remain.quantity_per_unit
            analitic_remain.quantity = analitic_remain.quantity\
                - (wiz.product_qty * analitic_remain.quantity_per_unit)
            history = remain_history.search([('date', '=', today)])
            if not history:
                remain_history.create({
                    'date': today,
                    'qty_per_unit': analitic_remain.quantity_per_unit})
    '''

    @api.multi
    def get_last_productions(self, analitic_remain, today):
        productions_obj = self.env['mrp.production']
        ref_day = (datetime.today() - timedelta(days=30)).strftime(DFORMAT)
        last_prod = productions_obj.search([
            ('date_finished', '>', ref_day)])
        analitic_remain.last_calc = today
        if len(last_prod) < 15:
            ref_day = today - timedelta(days=15)
            last_prod = productions_obj.search([
                ('date_finished', '>', ref_day)])
            if len(last_prod) < 8:
                analitic_remain.quantity_per_unit = 0
            else:
                self.get_unit_remain(analitic_remain, last_prod, 15)
        else:
            self.get_unit_remain(analitic_remain, last_prod, 30)

    @api.multi
    def get_unit_remain(self, analitic_remain, last_prod, days):
        qty = 0
        for prod in last_prod:
            qty = qty + prod.product_qty
        if days == 15:
            qty = qty * 2
        analitic_remain.quantity_per_unit = analitic_remain.quantity/qty
