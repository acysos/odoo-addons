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

    tracked = fields.Boolean(string='Tracked', default=False)

    def _get_sale_line(self, cr, uid, proc, checked, context=None):
            domain = [('product_id', '=', proc.product_id.id),
                      ('product_qty', '=', proc.product_qty),
                      ('id', 'not in', checked),
                      ('state', 'in', ['running', 'done'])]
            if proc.group_id:
                domain.append(('group_id', '=', proc.group_id.id))
            proc_ids = self.search(cr, uid, domain)
            if len(proc_ids) > 0:
                proc_orig = self.browse(cr, uid, proc_ids, context)[0]
                sale_line_id = False
                if proc_orig:
                    if proc_orig.sale_line_id:
                        sale_line_id = proc_orig.sale_line_id.id
                    if sale_line_id:
                        return sale_line_id
                    else:
                        checked.append(proc_orig.id)
                        self._get_sale_line(cr, uid, proc_orig, checked,
                                            context)
                else:
                    return False
            return False

    def run_scheduler(self, cr, uid, use_new_cursor=False, company_id=False,
                      context=None):
        if not context:
            context = {}
        context['scheduler'] = True
        super(ProcurementOrder, self).run_scheduler(cr, uid, use_new_cursor,
                                                    company_id, context)

        proc_ids = self.search(cr, uid,
                               [('state', '=', 'running'),
                                ('purchase_line_id', '!=', False),
                                ('tracked', '!=', True)])

        purchase_track_obj = self.pool.get('purchase.tracking')
        for proc in self.browse(cr, uid, proc_ids, context):
            sale_line_id = self._get_sale_line(cr, uid, proc, [proc.id],
                                               context)
            if sale_line_id:
                track_ids = purchase_track_obj.search(
                    cr, uid,
                    [('purchase_line_id', '=', proc.purchase_line_id.id)])
                if len(track_ids) == 0:
                    vals = {
                        'purchase_line_id': proc.purchase_line_id.id,
                        'sale_line_id': sale_line_id,
                    }

                    purchase_track_obj.create(cr, uid, vals, context)
                    self.write(cr, uid, proc.id, {'tracked': True}, context)
                    cr.commit()

        return {}
