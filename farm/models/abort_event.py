# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AbortEvent(models.Model):
    _name = 'farm.abort.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}
    _auto = True

    female_cycle = fields.Many2one(
        comodel_name='farm.animal.female_cycle', string='Female Cycle')

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise Warning(
                _("Only females can abort"))
        if not self.is_ready():
            raise Warning(
                _("Only pregnat females can abort"))
        self.female_cycle = self.animal.current_cycle
        self.animal.update_state()
        self.animal.current_cycle.update_state(self)
        super(AbortEvent, self).confirm()

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
