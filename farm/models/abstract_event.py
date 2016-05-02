# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

EVENT_STATES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ]


class AbstractEvent(models.Model):
    _name = 'farm.event'
    _auto = False

    animal_type = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),
        ('individual', 'Individual'), ('group', 'Group'),
        ], string="Animal Type", select=True)
    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             select=True, default='get_specie')
    farm = fields.Many2one(comodel_name='stock.location', string='Farm',
                           domain=[('usage', '=', 'view'), ])
    job_order = fields.Many2one(comodel_name='farm.event.order',
                                string='Order')
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             select=True)
    animal_group = fields.Many2one(comodel_name='farm.animal.group',
                                   string='Group')
    lot = fields.Many2one(comodel_name='stock.production.lot', string='Lot',
                          compute='get_lot')
    timestamp = fields.Datetime(string='Date & Time', required=True,
                                default=fields.Datetime.now())
    employee = fields.Many2one(comodel_name='res.users', String='Employee',
                               help='Employee that did the job.')
    notes = fields.Text(string='Notes')
    state = fields.Selection(string='State', selection=EVENT_STATES,
                             default='draft')

    @api.one
    def get_lot(self):
        if self.animal_type == 'group':
            for lot in self.animal_group.lot:
                self.lot = lot.lot
        else:
            self.lot = self.animal.lot.lot

    @api.one
    def confirm(self):
        self.state = 'validated'
        return True

    @api.one
    @api.onchange('timestamp')
    def set_defaults(self):
        if len(self.job_order) > 0:
            self.specie = self.job_order.specie
            self.animal_type = self.job_order.animal_type
            self.farm = self.job_order.farm
        else:
            for animal in self.animal:
                self.specie = animal.specie
                self.animal_type = animal.type
                self.farm = animal.location.location_id


class ImportedEventMixin(models.Model):
    _name = 'farm.event.import.mixin'
    _inherit = {'farm.event': 'AbstractEvent_id'}

    imported = fields.Boolean(string='Imported', default=False)
