# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class PregnancyDiagnosisEvent(models.Model):
    _name = 'farm.pregnancy_diagnosis.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}
    _auto = True

    result = fields.Selection([
        ('negative', 'Negative'), ('positive', 'Positive'),
        ('nonconclusive', 'Non conclusive'),
        ('not-pregnant', 'Observed not Pregnant'), ],
        string='Result',
        required=True, default='positive')
    female_cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                                   string='Female Cycle')

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise Warning(
                _("Only females can be diagnosed"))
        if not self.is_ready():
            raise Warning(
                _("Only mated females can be diagnosed"))
        self.female_cycle = self.animal.current_cycle
        self.animal.update_state()
        self.animal.current_cycle.update_state(self)
        super(PregnancyDiagnosisEvent, self).confirm()

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.animal.current_cycle.state == 'mated':
            return True
        else:
            return False
