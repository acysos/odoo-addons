# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _


class Wizard(models.TransientModel):
    _name = 'farm.animal.wizard'

    def _default_animal(self):
        return self.env['farm.animal'].browse(self._context.get('active_id'))

    animal = fields.Many2one(comodel_name='farm.animal', requiered=True,
                             default=_default_animal)
    female_sequence = fields.Char(string='Mother id', requiered=True)
    location_dest = fields.Many2one(comodel_name='stock.location',
                                    string='Mother destination',
                                    domain=[('usage', '=', 'internal')],
                                    requiered=True)

    @api.multi
    def PromoteMother(self):
        for res in self:
            res.animal.female_sequence = res.female_sequence
            res.animal.location = res.location_dest
        return {}


class Animal(models.Model):
    _inherit = 'farm.animal'
    _order = 'ifr_sequence'

    ifr_sequence = fields.Char(string='Female Sequence')

    @api.multi
    def launch_wizard(self):
        context = self.env.context.copy()
        context['active_ids'] = self.ids
        wizard_model = 'farm.animal.wizard'
        return {
            'name': _('Promote mother'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wizard_model,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            }
        return {}
