# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MoveEvent(models.Model):
    _name = 'farm.move.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}
    _auto = True

    from_location = fields.Many2one(comodel_name='stock.location',
                                    string='Origin', required=True,
                                    domain=[('usage', '=', 'internal'),
                                            ('silo', '=', False), ])
    to_location = fields.Many2one(comodel_name='stock.location',
                                  string='Destination', required=True,
                                  domain=[('usage', '=', 'internal'),
                                          ('silo', '=', False), ])
    quantity = fields.Integer(string='Quantity', required=True,
                              default=1)
    unit_price = fields.Float(string='Unit Price', required=True,
                              digits=(16, 4),
                              help='Unitary cost of Animal or Group for'
                              'analytical accounting.')
    uom = fields.Many2one(comodel_name='product.uom', string='UOM')
    weight = fields.Float(string='Weight', digits=(16, 2))
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move',
                           readonly=True)
    weight_record = fields.Selection(
        string='Weight Record',
        selection=[(None, ''),
                   ('farm.animal.weight', 'Animal Weight'),
                   ('farm.animal.group.weight', 'Group Weight'), ],
        readonly=True)
