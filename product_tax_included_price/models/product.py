# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class product_product(models.Model):
    _inherit = "product.product"

    @api.one
    @api.depends(
        'lst_price', 'taxes_id'
    )
    def _product_lst_price_tax(self):
        partner = self.company_id.partner_id
        price = self.lst_price
        taxes = self.taxes_id.compute_all(price, 1, self, partner, False)
        self.lst_price_tax = taxes['total_included']
        
    
    lst_price_tax = fields.Float(string='Public Tax Included',
                                 digits=dp.get_precision('Product Price'),
                                 readonly=True,
                                 compute='_product_lst_price_tax')
