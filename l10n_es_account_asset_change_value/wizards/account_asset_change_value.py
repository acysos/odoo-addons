# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, exceptions


class AccountAssetChangeValue(models.TransientModel):

    _name = 'account.asset.change.value'

    change_date = fields.Date(string='Change Date', required=True)
    change_value = fields.Float(string='Change Value', required=True)

    @api.multi
    def action_change_value(self):
        self.ensure_one()
        asset_id = self.env.context.get('active_id')
        asset = self.env['account.asset.asset'].browse(asset_id)
        asset.update_asset(self.change_date, self.change_value)
        return True
