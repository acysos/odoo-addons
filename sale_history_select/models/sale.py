# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2014 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
from openerp import models, fields, api
from openerp.tools.translate import _

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    order_line_id = fields.Many2one(comodel_name='sale.order.line',
                                    string='Product', required=False,
                                    states={'draft': [('readonly', False)]})
    
    def onchange_order_line_id(self, cr, uid, ids, order_line_id, context=None):
        line = self.browse(cr, uid, order_line_id, context)

        return {'value':{'name': line.name, 'price_unit': line.price_unit,
                'discount': line.discount }}
        
    def name_get(self, cr, uid, ids, context=None):
        res = super(sale_order_line, self).name_get(cr, uid, ids, context)
        res = []
        for line in self.browse(cr, uid, ids, context):
            name = line.order_id.date_order or '' + '-' + line.name + ' - ' + str(line.product_uom_qty) + ' - ' + str(line.price_unit) + ' - ' + line.order_partner_id.name
            res.append((line.id, name))
        return res
        