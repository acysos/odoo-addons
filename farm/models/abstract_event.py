# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

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
        ], string="Animal Type", select=True, default='group')
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
    lot = fields.Many2one(comodel_name='stock.lot', string='Lot',
                          compute='get_lot')
    timestamp = fields.Datetime(string='Date & Time', required=True,
                                default=fields.Datetime.now())
    employee = fields.Many2one(comodel_name='res.users', String='Employee',
                               help='Employee that did the job.')
    notes = fields.Text(string='Notes')
    state = fields.Selection(string='State', selection=EVENT_STATES,
                             default='draft')

    def get_lot(self):
        for res in self:
            if res.animal_type == 'group':
                for lot in res.animal_group.lot:
                    res.lot = lot.lot
            else:
                res.lot = res.animal.lot.lot

    def confirm(self):
        for res in self:
            res.state = 'validated'
        return True

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
            for animal in self.animal_group:
                self.specie = animal.specie
                self.animal_type = animal.type
                self.farm = animal.location.location_id


class ImportedEventMixin(models.Model):
    _name = 'farm.event.import.mixin'
    _inherit = {'farm.event': 'AbstractEvent_id'}

    imported = fields.Boolean(string='Imported', default=False)
