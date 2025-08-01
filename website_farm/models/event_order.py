# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from odoo.exceptions import ValidationError

class FarmEventOrder(models.Model):
    _inherit = 'farm.event.order'

    def next_farrowing(self, employee, values):
        female = self.env['farm.animal'].search([('label', '=', values['farm_label'])])
        if not female:
            return {'error': 'Animal not found'}
        order = self.env['farm.event.order'].browse(values['order_id'])
        if not order.farrowing_events:
            order.farm = female.farm
        labels = []
        if values['label1']:
            labels.append(values['label1'])
            if values['label2']:
                labels.append(values['label2'])
                if values['label3']:
                    labels.append(values['label3'])
                    if values['label4']:
                        labels.append(values['label4'])
                        if values['label5']:
                            labels.append(values['label5'])
        animal_labels = []
        for label in labels:
            animal_label = self.env['farm.tags'].search([('name', '=', label)])
            if not animal_label:
                animal_label = self.env['farm.tags'].create({'name': label})
            animal_labels.append(animal_label)
        self.env['farm.farrowing.event'].create({
            'order': order.id,
            'live': values['live'],
            'new_tags': labels[(6, 0, [x.id for x in animal_labels])] if labels else False,
            'animal_type': 'female',
            'farm': female.farm.id,
            'animal': female.id,
            'specie': female.specie.id,
            'timestamp': fields.datetime.now(),
            'employee': employee
        })
        return False
