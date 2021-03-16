# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class WizardUpdateChartsAccounts(models.TransientModel):
    _inherit = 'wizard.update.charts.accounts'

    def diff_fields(self, template, real):
        result = super(WizardUpdateChartsAccounts, self).diff_fields(
            template, real)
        for key, field in template._fields.items():
            if 'aeat.sii.mapping.registration.keys' == field.get_description(
                    self.env).get("relation", ""):
                try:
                    if template[key] != real[key]:
                        result[key] = template[key]
                except KeyError:
                    pass
        return result
