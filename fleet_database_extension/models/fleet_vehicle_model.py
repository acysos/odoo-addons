# -*- coding: utf-8 -*-
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class FleetVehicleModelSerialYear(models.Model):
    _name = 'fleet.vehicle.model.serial.year'
    
    name = fields.Integer(string='Year')

    _sql_constraints = [
        ('name_uniq',
         'unique (name)',
         'This year exist, select it instead of create a new year.')
    ]


class FleetVehicleModelSerialEquip(models.Model):
    _name = 'fleet.vehicle.model.serial.equip'
    
    name = fields.Char(string='Name')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_uniq',
         'unique (name)',
         'This equipment exist, select it instead of create a new equipment.')
    ]


class FleetVehicleModelSerialWheel(models.Model):
    _name = 'fleet.vehicle.model.serial.wheel'
    
    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    
    _sql_constraints = [
        ('name_uniq',
         'unique (name)',
         'This wheel exist, select it instead of create a new wheel.')
    ]


class FleetVehicleModelSerialExhaustPipe(models.Model):
    _name = 'fleet.vehicle.model.serial.exhaust.pipe'
    
    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    
    _sql_constraints = [
        ('name_uniq',
         'unique (name)',
         'This exhaust pipe exist, select it instead of create a new exhaust.')
    ]


class FleetVehicleModelSerial(models.Model):
    _name = 'fleet.vehicle.model.serial'
    
    model_id = fields.Many2one(comodel_name='fleet.vehicle.model',
                               string='Model', required=True)
    name = fields.Char(string='Serial Number')
    year = fields.Many2one(comodel_name='fleet.vehicle.model.serial.year',
                           string='Year')
    doors = fields.Integer(string='Doors Number',
                           help='Number of doors of the vehicle', default=5)
    transmission = fields.Selection(
        selection=[('manual', 'Manual'), ('automatic', 'Automatic')], 
        string='Transmission', help='Transmission Used by the vehicle')
    fuel_type = fields.Selection(
        selection=[('gasoline', 'Gasoline'), ('diesel', 'Diesel'),
                   ('electric', 'Electric'), ('hybrid', 'Hybrid')],
         string='Fuel Type', help='Fuel Used by the vehicle')
    horsepower = fields.Integer(string='Horsepower')
    power = fields.Integer(string='Power', help='Power in kW of the vehicle')
    co2 = fields.Float(string='CO2 Emissions',
                       help='CO2 emissions of the vehicle')
    equip = fields.Many2one(comodel_name='fleet.vehicle.model.serial.equip',
                            string='Equipment')
    wheel = fields.Many2one(comodel_name='fleet.vehicle.model.serial.wheel',
                            string='Wheel')
    exhaust_pipe = fields.Many2one(
        comodel_name='fleet.vehicle.model.serial.exhaust.pipe',
        string='Exhaust Pipe')
    notes = fields.Text(string='Notes')
