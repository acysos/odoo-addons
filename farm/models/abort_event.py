# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning


class AbortEvent(models.Model):
    _name = 'farm.abort.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}
    _auto = True

    female_cycle = fields.Many2one(
        comodel_name='farm.animal.female_cycle', string='Female Cycle')


    def confirm(self):
        for res in self:
            if not res.is_compatible():
                raise Warning(
                    _("Only females can abort"))
            if not res.is_ready():
                raise Warning(
                    _("Only pregnat females can abort"))
            res.female_cycle = res.animal.current_cycle
            res.animal.update_state()
            res.animal.current_cycle.update_state(res)
            super(AbortEvent, res).confirm()

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.animal.current_cycle.state == 'pregnat':
            return True
        else:
            return False
