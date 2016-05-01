# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (c) 2011  NaN Projectes de Programari Lliure S.L.
#                   (http://www.nan-tic.com) All Rights R
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

from datetime import datetime
from openerp import netsvc
import time
from openerp import tools, api
from openerp.osv.orm import browse_record, browse_null

from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp

class product_pricelist(orm.Model):
    _inherit = 'product.pricelist'

    _columns ={
        'visible_discount': fields.boolean('Visible Discount'),
    }
    _defaults = {
         'visible_discount': True,
    }


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def action_cancel_draft(self, cr, uid, ids, *args):
        super(purchase_order, self).action_cancel_draft(cr, uid,
            ids, *args)
        line_obj = self.pool.get('purchase.order.line')
        for order in self.browse(cr, uid, ids):
            for line in order.order_line:
                line_obj.write(cr, uid, [line.id], {'state': 'draft'})
        return True

    def inv_line_create(self, cr, uid, a, ol):
        result = super(purchase_order, self).inv_line_create(cr, uid, a, ol)
        result[2]['discount1'] = ol.discount1 or 0.0
        result[2]['discount2'] = ol.discount2 or 0.0
        result[2]['discount3'] = ol.discount3 or 0.0
        return result
    
    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of purchase orders.
        Orders will only be merged if:
        * Purchase Orders are in draft
        * Purchase Orders belong to the same partner
        * Purchase Orders are have same stock location, same pricelist
        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new purchase order id
        """
        #TOFIX: merged order line should be unlink
        wf_service = netsvc.LocalService("workflow")
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'move_dest_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

    # compute what the new orders should contain

        new_orders = {}

        for porder in [order for order in self.browse(cr, uid, ids, context=context) if order.state == 'draft']:
            order_key = make_key(porder, ('partner_id', 'location_id', 'pricelist_id'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'partner_address_id': porder.partner_address_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'warehouse_id': porder.warehouse_id.id,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position and porder.fiscal_position.id or False,
                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (order_infos['notes'] or '') + ('\n%s' % (porder.notes,))
                if porder.origin:
                    if not porder.origin in order_infos['origin'] and not order_infos['origin'] in porder.origin:
                        order_infos['origin'] = (order_infos['origin'] or '') + ' ' + porder.origin

            for order_line in porder.order_line:
                line_key = make_key(order_line, ('name', 'date_planned',
                     'taxes_id', 'price_unit', 'notes', 'product_id',
                     'move_dest_id', 'account_analytic_id', 'discount1',
                     'discount2','discount3'))
                o_line = order_infos['order_line'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += order_line.product_qty * order_line.product_uom.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(order_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = order_line.product_uom and order_line.product_uom.factor or 1.0



        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(0, 0, value) for value in order_data['order_line'].itervalues()]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(uid, 'purchase.order', old_id, 'purchase_cancel', cr)
        return orders_info


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'discount1': fields.float('Discount 1', digits=(10, 2)),
        'discount2': fields.float('Discount 2', digits=(10, 2)),
        'discount3': fields.float('Discount 3', digits=(10, 2)),
        'discount': fields.float('Calculated discount', digits=(10, 2),
                                  readonly="True"),
    }

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft',
                            context=None):

        def get_real_price(res_dict, product_id, qty, uom, pricelist):
            item_obj = self.pool.get('product.pricelist.item')
            price_type_obj = self.pool.get('product.price.type')
            product_obj = self.pool.get('product.product')
            template_obj = self.pool.get('product.template')
            field_name = 'standard_price'

            if res_dict.get('item_id', False) and res_dict['item_id'].get(
                                                             pricelist, False):
                item = res_dict['item_id'].get(pricelist, False)
                item_base = item_obj.read(cr, uid, [item], ['base'])[0]['base']
                if item_base > 0:
                    field_name = price_type_obj.browse(cr,
                                                       uid, item_base).field

            product = product_obj.browse(cr, uid, product_id, context)
            product_tmpl_id = product.product_tmpl_id.id

            product_read = template_obj.read(cr, uid, product_tmpl_id,
                                             [field_name], context)

            factor = 1.0
            if uom and uom != product.uom_po_id.id:
                product_uom_obj = self.pool.get('product.uom')
                uom_data = product_uom_obj.browse(cr, uid,
                                                  product.uom_po_id.id)
                factor = uom_data.factor
            return product_read[field_name] / factor

        res = super(purchase_order_line, self).onchange_product_id(
                            cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order,
                            fiscal_position_id, date_planned,
                            name, price_unit, state,
                            context)

        res_partner = self.pool.get('res.partner')
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
        else:
            lang = False
        context = {'lang': lang, 'partner_id': partner_id}
        result = res['value']

        pricelist_obj = self.pool.get('product.pricelist')
        product_obj = self.pool.get('product.product')

        if product_id:
            product = product_obj.browse(cr, uid, product_id, context=context)
            if result.get('price_unit', False):
                price = result['price_unit']
            else:
                return res

            product = product_obj.browse(cr, uid, product_id, context)
            list_price = pricelist_obj.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id, {'uom': uom_id,
                                                         'date': date_order})

            pricelists = pricelist_obj.read(cr, uid, [pricelist_id],
                                            ['visible_discount'])

            new_list_price = get_real_price(list_price, product.id, qty,
                                            uom_id, pricelist_id)

            if(len(pricelists) > 0 and pricelists[0]['visible_discount'] and
               list_price[pricelist_id] != 0):
                discount = (new_list_price - price) / new_list_price * 100
                result['price_unit'] = new_list_price
                result['discount1'] = discount
            else:
                result['discount1'] = 0.0

        return res

    def _get_discount(self, cr, uid, ids, field_name, field_value, context):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            value = 100 * (1 - ((100 - line.discount1) / 100.00 *
                (100 - line.discount2) / 100.00 * (100 - line.discount3) / 100.00))
            result[line.id] = value
        return result

    def onchange_discount(self, cr, uid, ids, discount1, discount2,
                          discount3, context=None):
        if context is None:
            context = {}
        result = {'value': {}}
        result['value']['discount'] = 100 * (1 - ((100 - discount1) / 100.00 *
                          (100 - discount2) / 100.00 * (100 - discount3) / 100.00))
        return result

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        
        for line in self.browse(cr, uid, ids, context=context):
            value = 100 * (1 - ((100 - vals.get('discount1', line.discount1)) /
                100.00 * (100 - vals.get('discount2', line.discount2)) / 100.00 *
                (100 - vals.get('discount3', line.discount3)) / 100.00))
            print value
            vals['discount'] = value
            if not super(purchase_order_line, self).write(cr, uid, [line.id],
                                                   vals, context=context):
                return False

        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        vals['discount'] = 100 * (1 - ((100 - vals.get('discount1', 0)) /
            100.00 * (100 - vals.get('discount2', 0)) / 100.00 * (100 -
            vals.get('discount3', 0)) / 100.00))
        return super(purchase_order_line, self).create(cr, uid, vals, context)

    def _get_sale_order_state(self, cr, uid, ids, context=None):
        result = {}
        for order in self.pool.get('sale.order').browse(cr, uid, ids,
                                                        context=context):
            for line in order.order_line:
                result[line.id] = True
        return result.keys()


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _get_discount_invoice(self, cursor, user, move_line):
        #if move_line.sale_line_id:
            #return move_line.sale_line_id.discount
        if move_line.purchase_line_id:
            line = move_line.purchase_line_id
            return 100 * (1 - ((100 - line.discount1) / 100.00 * (100 -
                       line.discount2) / 100.00 * (100 - line.discount3) / 100.00))
        return super(stock_picking, self)._get_discount_invoice(cursor, user,
                                                                move_line)

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        if move_line.sale_line_id:
            self.pool.get('account.invoice.line').write(cr, uid,
                [invoice_line_id], {
                    'discount1': move_line.sale_line_id.discount,
                })
        if move_line.purchase_line_id:
            self.pool.get('account.invoice.line').write(cr, uid,
                 [invoice_line_id], {
                    'discount': move_line.purchase_line_id.discount,
                    'discount1': move_line.purchase_line_id.discount1,
                    'discount2': move_line.purchase_line_id.discount2,
                    'discount3': move_line.purchase_line_id.discount3,
                    })
        return super(stock_picking, self)._invoice_line_hook(cr, uid,
                                                 move_line, invoice_line_id)


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    _columns = {
        'discount': fields.float('Calculated discount', digits=(10, 2),
                                 readonly="True"),
        'discount1': fields.float('Discount 1', digits=(10, 2)),
        'discount2': fields.float('Discount 2', digits=(10, 2)),
        'discount3': fields.float('Discount 3', digits=(10, 2)),
    }

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        print company_id
        res = super(account_invoice_line, self).product_id_change(product, uom_id, qty, name, type,
            partner_id, fposition_id, price_unit, currency_id,
            company_id)

        def get_real_price(res_dict, product_id, qty, uom, pricelist):
            item_obj = self.pool.get('product.pricelist.item')
            price_type_obj = self.pool.get('product.price.type')
            product_obj = self.pool.get('product.product')
            template_obj = self.pool.get('product.template')
            field_name = 'list_price'

            if res_dict.get('item_id',False) and res_dict['item_id'].get(pricelist,False):
                item = res_dict['item_id'].get(pricelist,False)
                item_base = item_obj.read(cr, uid, [item], ['base'])[0]['base']
                if item_base > 0:
                    field_name = price_type_obj.browse(cr, uid, item_base).field

            product = product_obj.browse(cr, uid, product_id, context)
            product_tmpl_id = product.product_tmpl_id.id

            product_read = template_obj.read(cr, uid, product_tmpl_id, [field_name], context)

            factor = 1.0
            if uom and uom != product.uom_id.id:
                product_uom_obj = self.pool.get('product.uom')
                uom_data = product_uom_obj.browse(cr, uid,  product.uom_id.id)
                factor = uom_data.factor
            return product_read[field_name] * factor

        if product:
            pricelist_obj = self.pool.get('product.pricelist')
            partner_obj = self.pool.get('res.partner')
            product = self.pool.get('product.product').browse(cr, uid, product, context=context)
            result = res['value']
            pricelist = False
            real_price = 0.00
            if type in ('in_invoice', 'in_refund'):
                if not price_unit and partner_id:
                    pricelist =partner_obj.browse(cr, uid, partner_id).property_product_pricelist_purchase.id
                    if not pricelist:
                        raise osv.except_osv(_('No Purchase Pricelist Found!'),_("You must first define a pricelist on the supplier form!"))
                    price_unit_res = pricelist_obj.price_get(cr, uid, [pricelist], product.id, qty or 1.0, partner_id, {'uom': uom})
                    price_unit = price_unit_res[pricelist]
                    real_price = get_real_price(price_unit_res, product.id, qty, uom, pricelist)
            else:
                if partner_id:
                    pricelist = partner_obj.browse(cr, uid, partner_id).property_product_pricelist.id
                    if not pricelist:
                        raise osv.except_osv(_('No Sale Pricelist Found!'),_("You must first define a pricelist on the customer form!"))
                    price_unit_res = pricelist_obj.price_get(cr, uid, [pricelist], product.id, qty or 1.0, partner_id, {'uom': uom})
                    price_unit = price_unit_res[pricelist]

                    real_price = get_real_price(price_unit_res, product.id, qty, uom, pricelist)
            if pricelist:
                pricelists=pricelist_obj.read(cr,uid,[pricelist],['visible_discount'])
                if(len(pricelists)>0 and pricelists[0]['visible_discount'] and real_price != 0):
                    discount=(real_price-price_unit) / real_price * 100
                    result['price_unit'] = real_price
                    result['discount1'] = discount
                else:
                    result['discount1'] = 0.0

        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        for line in self.browse(cr, uid, ids, context=context):
            discount1 = vals.get('discount1', line.discount1) or 0.0
            discount2 = vals.get('discount2', line.discount2) or 0.0
            discount3 = vals.get('discount3', line.discount3) or 0.0
            value = 100 * (1 - ((100 - discount1) / 100.00 * (100 - discount2) /
                                100 * (100 - discount3) / 100.00))
            vals['discount'] = value
            if not super(account_invoice_line, self).write(cr, uid, [line.id],
                                                    vals, context=context):
                return False

        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        vals['discount'] = 100 * (1 - ((100 - vals.get('discount1', 0)) / 100.00 *
            (100 - vals.get('discount2', 0)) / 100.00 * (100 -
            vals.get('discount3', 0)) / 100.00))
        return super(account_invoice_line, self).create(cr, uid, vals,
                                                          context)

    def _get_discount(self, cr, uid, ids, field_name, field_value, context):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            value = 100 * (1 - ((100 - line.discount1) / 100.00 * (100 -
                        line.discount2) / 100.00 * (100 - line.discount3) / 100.00))
            result[line.id] = value
        return result

    def onchange_discount(self, cr, uid, ids, discount1, discount2, discount3,
                          context=None):
        if context is None:
            context = {}
        result = {'value': {}}
        result['value']['discount'] = 100 * (1 - ((100 - discount1) / 100.00 *
                          (100 - discount2) / 100.00 * (100 - discount3) / 100.00))
        return result

