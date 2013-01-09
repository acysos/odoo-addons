# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (c) 2013 Mikel Martin <info@zhenit.com>
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

from osv import fields, osv
from tools.translate import _
import tools

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, uid,
            ids, journal_id, group, type, context)
        for picking_id, invoice_id in res.items():
            inv_obj = self.pool.get("account.invoice")
            invoice = inv_obj.browse(cr, uid, invoice_id)
            result = inv_obj.onchange_partner_id(cr, uid, invoice_id,
                invoice.type, invoice.partner_id.id, invoice.date_invoice,
                invoice.payment_term, invoice.partner_bank_id, invoice.company_id.id)
            inv_obj.write(cr, uid, invoice_id, result['value'])
        return res
    
stock_picking()