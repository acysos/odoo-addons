# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from osv import osv, fields
from tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    
    def update_draft_invoices(self, cr, uid, ids, vals, context=None):
        draft_invs = self.pool.get('account.invoice').search(cr,uid,[('state','=','draft')])
        product = self.pool.get('product.product').browse(cr,uid,ids[0])
        for invoice in self.pool.get('account.invoice').browse(cr,uid,draft_invs):
            for line in invoice.invoice_line:
                if line.product_id.id == product.id:
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [invoice.partner_id.property_product_pricelist.id],
                    line.product_id.id, line.quantity or 1.0, invoice.partner_id.id, {
                        'uom': line.uos_id.id,
                        'date': invoice.date_invoice,
                        })[invoice.partner_id.property_product_pricelist.id]
                    self.pool.get('account.invoice.line').write(cr,uid,[line.id],{'price_unit':price})
                    invoice.button_reset_taxes()
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_template,self).write(cr, uid, ids, vals, context)
        self.update_draft_invoices(cr, uid, ids, context)
        return res
    
product_template()