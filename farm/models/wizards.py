# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _


class farmOperationsFatten(models.TransientModel):
    _name = 'farm.operations.fatten.wizard'

    farm = fields.Many2one(comodel_name='stock.location', string='Origin',
                           domain=[('usage', '"', 'view')])
    animal_group = fields.Many2one(comodel_name='farm.animal.group',
                                   string='Animal Group')
    dest_farm = fields.Many2one(comodel_name='stock.location',
                                string='Destination',
                                domain=[('usage', '"', 'view')])
    weight = fields.Float(string='Weight (kg)')
    truck_registration = fields.Many2one(comodel_name='farm.trucks',
                                         string='Truck registration')
    driver_registration = fields.Many2one(comodel_name='farm.drivers',
                                          string='Driver Registration')

    @api.multi
    def confirm(self):
        trans_obj = self.env['farm.transition.event']
        w_order_obj = self.env['farm.event.order']
        locs_obj = self.env['stock.location']
        specie = self.env['farm.specie'].search([(True, '=', True)])[0]
        for res in self:
            dest_farm_locs = locs_obj.search([(
                'location_id', '=', res.farm.id)])
            dest_farm_locs_ids = []
            for loc in dest_farm_locs:
                dest_farm_locs_ids.append(loc)
            dest_loc = locs_obj.search([
                ('farm_yard', '=', True),
                ('location_id','in', dest_farm_locs_ids)])
            new_w_order = w_order_obj.create({
                'animal_type': 'group',
                'specie': specie.id,
                'event_type': 'trasformation_event',
                'farm': res.farm.id,
                })
            trans_obj.create({
                })
        return {}


class farmTruck(models.Model):
    _name = 'farm.truks'
    
    truck_registration = fields.Char(string='Truck registration')


class farmDriver(models.Model):
    _name = 'farm.drivers'

    driver_registration = fields.Char(string='Driver Registration')
    driver_name = fields.Char(string='Driver Name')