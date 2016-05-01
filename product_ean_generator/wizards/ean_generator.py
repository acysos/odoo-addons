# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields
import openerp.addons.product.product

class ean_generator(models.Model):
    _name = 'ean.generator'
    
    def create_ean(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        for product in prod_obj.browse(cr, uid, context['active_ids'],
                                       context):
            ean13 = openerp.addons.product.product.sanitize_ean13(product.default_code)
            m_id =  product.id
            prod_obj.write(cr,uid,[m_id],{'ean13':ean13})
        return { 'type' : 'ir.actions.act_window_close' }