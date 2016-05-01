# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    @authors: Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
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


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'
    
    tracked = fields.Boolean(string='Tracked',default=False)
    
    def _get_sale_line(self, cr, uid, proc, checked, context=None):
            res = super(ProcurementOrder, self)._get_sale_line(cr, uid, proc,
                                                               checked,
                                                               context)
            if not res:
                mrp_prod_obj = self.pool.get('mrp.production')
                mrp_prod_ids = mrp_prod_obj.search(cr, uid, [('state','=',
                                                              'confirmed')])
                for mrp in mrp_prod_obj.browse(cr, uid, mrp_prod_ids, context):
                    found = False
                    for prod_line in mrp.product_lines:
                        if prod_line.product_id.id == proc.product_id.id and \
                        prod_line.product_qty == proc.product_qty:
                            found = True
                    if found:
                        domain = [('production_id','=',mrp.id),
                                  ('id','not in', checked),]
                        proc_ids = self.search(cr, uid, domain)
                        if len(proc_ids) > 0:
                            proc_orig = self.browse(cr, uid, proc_ids,
                                                    context)[0]
                            sale_line_id = False
                            if proc_orig:
                                if proc_orig.sale_line_id:
                                    sale_line_id = proc_orig.sale_line_id.id
                                if sale_line_id:
                                    res = sale_line_id
                                else:
                                    checked.append(proc_orig.id)
                                    res = self._get_sale_line(cr, uid, proc_orig, checked, context)
            return res
        