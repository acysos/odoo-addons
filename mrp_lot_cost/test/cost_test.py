# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase
from openerp import exceptions


class TestMrpLotCost:

    def setUp(self):
        super(TestMrpLotCost, self).setUp()
        '''models'''
        self.product_model = self.env['product.product']
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.purchase_model = self.env['purchase.order']
        self.pur_line_model = self.env['purchase.order']
        self.lot_model = self.env['stock.production.lot']
        self.partner_model = self.env['res.partner']
        '''objects'''
        self.raw_material = self.product_model.create({'name': 'raw_mat'})
        self.manu_material = self.product_model.create({'name': 'manu_mat'})
        self.bom1 = self.bom_model.create({'name': 'manu_bom',
                                           'product_id': self.manu_material.id,
                                           'product_qty': 2})
        self.partner1 = self.partner_model.create({'name': 'partner1'})
        self.demo_pur = self.purchase_model.create({
            'partner_id': self.partner1.id,
            })
        self.pur_line1 = self.pur_line_model.create(
            {'order_id': self.demo_pur.id,
             'price_unit': 3,
             })