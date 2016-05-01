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
#############################################################################

import itertools
from lxml import etree
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def expand_extra_prices(self, cr, uid, ids, context={}):
        if type(ids) in [int, long]:
            ids = [ids]
        updated_invoices = []
        for invoice in self.browse(cr, uid, ids, context):
            fiscal_position = invoice.fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, invoice.fiscal_position.id, context) or False
            
            sequence = -1
            reorder = []
            for line in invoice.invoice_line:
                sequence += 1
                if sequence > line.sequence:
                    self.pool.get('account.invoice.line').write(cr, uid, [line.id], {
                        'sequence': sequence,
                    }, context)
                else:
                    sequence = line.sequence

                #if line.state != 'draft':
                    #continue
                if not line.product_id:
                    continue
                if line.extra_child_line_id:
                    continue
                
                if invoice.type in ['out_invoice','out_refund']:
                    extra_price = line.product_id.extra_price
                elif invoice.type in ['in_invoice','in_refund']:
                    extra_price = line.product_id.extra_price_purchase
#                     supplier_info_ids = self.pool.get('product.supplierinfo').search(cr, uid, [('name','=',line.invoice_id.partner_id.id),('product_id','=',line.product_id.id)])
#                     pl_partner_ids = self.pool.get('pricelist.partnerinfo').search(cr,uid,[('suppinfo_id','=',supplier_info_ids[0])], order='min_quantity DESC')
#                     pl_partner = self.pool.get('pricelist.partnerinfo').browse(cr,uid,pl_partner_ids)
#                     for pl in pl_partner:
#                         if pl.min_quantity <  line.quantity:
#                             extra_price = pl.extra_price
                if extra_price == 0:
                    continue
                
                sequence += 1
                tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, line.product_id.taxes_id)
                vals = {
                    'name': '-- '+(line.product_id.name_extra_price or ''),
                    'origin': line.origin,
                    'invoice_id': line.invoice_id.id,
                    'uos_id': line.uos_id.id,
                    'account_id': line.account_id.id,
                    'price_unit': extra_price,
                    'quantity': line.quantity,
                    'discount': line.discount,
                    'invoice_line_tax_id': [(6,0,tax_ids)],
                    'note': line.note,
                    'account_analytic_id': line.account_analytic_id.id or None,
                    'company_id': line.company_id.id,
                    'partner_id': line.partner_id.id,
                    'extra_parent_line_id': line.id,
                    'sequence': sequence,
                    'product_id': line.product_id.product_id_extra.id or None,
                }
                extra_line = self.pool.get('account.invoice.line').create(cr, uid, vals, context)
                print extra_line
                if not invoice.id in updated_invoices:
                    updated_invoices.append( invoice.id )

                self.pool.get('account.invoice.line').write(cr,uid,[line.id],{'extra_child_line_id':extra_line})

                for id in reorder:
                    sequence += 1
                    self.pool.get('account.invoice.line').write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)
            if context is None:
                context = {}
            ctx = context.copy()
            ait_obj = self.pool.get('account.invoice.tax')
            for id in ids:
                cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
                partner = self.browse(cr, uid, id, context=ctx).partner_id
                if partner.lang:
                    ctx.update({'lang': partner.lang})
                for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                    ait_obj.create(cr, uid, taxe)
        return
    
