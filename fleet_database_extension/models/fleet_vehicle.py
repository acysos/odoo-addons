# -*- coding: utf-8 -*-
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    model_serial_id = fields.Many2one(
        comodel_name='fleet.vehicle.model.serial',
        string='Serial model')

    @api.onchange('model_serial_id')
    def onchange_model_serial(self):
        self.doors = self.model_serial_id.doors
        self.fuel_type = self.model_serial_id.fuel_type
        self.transmission = self.model_serial_id.transmission
        self.horsepower = self.model_serial_id.horsepower
        self.power = self.model_serial_id.power
        self.co2 = self.model_serial_id.co2

