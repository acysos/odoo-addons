# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, models


class WizardUpdateChartsAccounts(models.TransientModel):
    _inherit = 'wizard.update.charts.accounts'

    def _is_different_fiscal_position(self, fp, fp_template, mapping_taxes,
                                      mapping_accounts):
        notes = super(
            WizardUpdateChartsAccounts, self)._is_different_fiscal_position(
                fp, fp_template, mapping_taxes, mapping_accounts)
        if fp.sii_registration_key_sale != \
                fp_template.sii_registration_key_sale:
            notes += _("The SII Sale registration is different")
        if fp.sii_registration_key_purchase != \
                fp_template.sii_registration_key_purchase:
            notes += _("The SII Purchase registration is different")
        return notes

    def _prepare_fp_vals(self, fp_template, mapping_taxes, mapping_accounts):
        res = super(WizardUpdateChartsAccounts, self)._prepare_fp_vals(
            fp_template, mapping_taxes, mapping_accounts)
        res['sii_registration_key_sale'] = \
            fp_template.sii_registration_key_sale.id
        res['sii_registration_key_purchase'] = \
            fp_template.sii_registration_key_purchase.id
        return res
