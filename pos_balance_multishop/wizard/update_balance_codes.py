# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _


class update_balance_codes(models.TransientModel):
    _name = 'wizard.update.balance.codes'

    def update_codes(self):
        if context is None:
            context = {}

        prod_obj = self.pool.get('product.product')
        code_obj = self.pool.get('product.balance.code')
        products = prod_obj.browse(self, context['active_ids'])

        for product in products:
            if len(product.balance_code_ids) > 0:
                for code in product.balance_code_ids:
                    if len(code.shop_id.balance_ids) > 0:
                        code_obj.remove_balance(cr, uid, [code.id], context)
                        code_obj.update_balance(cr, uid, [code.id], context)

        return {'type': 'ir.actions.act_window_close'}


