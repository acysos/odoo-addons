# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    balance_code_ids = fields.One2many(
        comodel_name='product.balance.code',
        inverse_name='product_id',
        string='Balance Codes')
    balance_type = fields.Selection(
        [('price', 'Price'), ('weight', 'Weight')], 'Type', select=True)
    balance_name = fields.Char(
        string='Code', readonly=False)
    balance_nomenclature = fields.Many2one(
        comodel_name='barcode.nomenclature', string='Nomenclature')
    balance_rule = fields.Many2one(comodel_name='barcode.rule', string='Rule')
    not_weighed = fields.Boolean('Not weighed', required=False)
    _sql_constraints = [
        ('balance_code_uniq', 'unique(balance_name, shop_id)',
         'The Balance Code must be unique per product and shop !'),
    ]
    
    
    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)

        code_obj = self.env['product.balance.code']
        for product in self:
            if len(product.balance_code_ids) > 0:
                for code in product.balance_code_ids:
                    if len(code.shop_id.balance_ids) > 0:
                        code_obj.remove_balance()
                        code_obj.update_balance()
        return res

    @api.multi
    @api.onchange('balance_name', 'balance_rule')
    def get_ean_code(self):
        barcode = False
        for product in self:
            if self.balance_rule and self.balance_name:
                ean = product.balance_rule.pattern[:2]
                ean += product.balance_name
                ean += '00000'
                code = list(ean)
                oddsum = evensum = total = control_digit = 0
                for i in range(len(code)):
                    if i % 2 == 0:
                        # even calculation
                        evensum += int(code[i])
                    else:
                        # odd calculation
                        oddsum += int(code[i])
                total = oddsum * 3 + evensum
                control_digit = int((10 - total % 10) % 10)
                barcode = ean + str(control_digit)
                product.barcode = barcode
    
    @api.multi
    def update_codes(self):
        for product in self:
            if len(product.balance_code_ids) > 0:
                for code in product.balance_code_ids:
                    if len(code.shop_id.balance_ids) > 0:
                        code.remove_balance()
                        code.update_balance()


class product_balance_code(models.Model):
    _name = 'product.balance.code'

    @api.multi
    def add_balance(self):
        for code in self:
            for balance in code.shop_id.balance_ids:
                if balance.network:
                    balance_con = getattr(
                        self, 'add_balance_' + balance.model_id.code)
                    balance_con(code, balance)

        return True

    @api.multi
    def update_balance(self):
        for code in self:
            for balance in code.shop_id.balance_ids:
                if balance.network:
                    balance_con = getattr(
                        self, 'update_balance_' + balance.model_id.code)
                    balance_con(code, balance)
        return True

    @api.multi
    def remove_balance(self):
        for code in self:
            for balance in code.shop_id.balance_ids:
                if balance.network:
                    balance_con = getattr(
                        self, 'remove_balance_' + balance.model_id.code)
                    balance_con(code, balance)
        return True

    product_id = fields.Many2one(
        comodel_name='product.template', string='Product', required=True)
    key = fields.Char(string='Key')
    shop_id = fields.Many2one(comodel_name='balance.sale.shop', string='Shop')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.onchange('balance_name', 'balance_rule')
    def get_ean_code(self):
        barcode = False
        for product in self:
            if self.balance_rule and self.balance_name:
                ean = product.balance_rule.pattern[:2]
                ean += product.balance_name
                ean += '00000'
                code = list(ean)

                oddsum = evensum = total = control_digit = 0
                for i in range(len(code)):
                    if i % 2 == 0:
                        # even calculation
                        evensum += int(code[i])
                    else:
                        # odd calculation
                        oddsum += int(code[i])
                total = oddsum * 3 + evensum

                control_digit = int((10 - total % 10) % 10)
                barcode = ean + str(control_digit)
                product.barcode = barcode

    @api.model
    def create(self, vals):
        res_id = super(ProductProduct, self).create(vals)
        res_id.balance_code_ids.add_balance()

        return res_id

    @api.multi
    def write(self, vals):
        self.balance_code_ids.remove_balance()
        res = super(ProductProduct, self).write(vals)
        self.balance_code_ids.update_balance()
        return res

    def unlink(self):
        self.balance_code_ids.remove_balance()
        res = super(ProductProduct, self).unlink()
        return res
    
    @api.multi
    def update_codes(self):
        for product in self:
            if len(product.balance_code_ids) > 0:
                for code in product.balance_code_ids:
                    if len(code.shop_id.balance_ids) > 0:
                        code.remove_balance()
                        code.update_balance()
    