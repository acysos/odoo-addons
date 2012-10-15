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

import netsvc

LOGGER = netsvc.Logger()
PRODUCT_TYPE_OUT_ORDER_LINE = ['configurable']

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    
    _columns = {
        'national_fiscal_position': fields.many2one('account.fiscal.position', 'National Fiscal Position',help='Default Fiscal position for the partners with fiscal address in the same country that the company'),
        'non_vat_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for non-Vat', help='Default Fiscal position for partners without vat number'),
        'valid_vies_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for Valid Vies Vat', help='Default Fiscal position for partners with a valid vat number in vies validation webservices'),
        'non_valid_vies_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for non-Valid Vies Vat', help='Default Fiscal position for partners without a valid vat number in vies validation webservices'),
        'non_european_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for non-European', help='Default Fiscal position for partners outside Europe'),
    }
sale_shop()

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def magento_create_order(self, cr, uid, sale_shop, values, context=None):
        """
        Create Magento Order
        Address, order line and amount is design by code.
        After you can add more order lines by base mapping
        :sale_shop: object
        :values: dicc order
        :return sale_order_id (OpenERP ID)
        """

        magento_external_referential_obj = self.pool.get('magento.external.referential')
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner.address')

        LOGGER.notifyChannel('Magento Sync Sale Order', netsvc.LOG_INFO, "Waiting Order %s ..." % (values['increment_id']))

        vals = {}
        confirm = False
        cancel = False
        customer_info = True
        magento_app = sale_shop.magento_website.magento_app_id

        """Partner OpenERP"""
        partner_id, customer_id = self.magento_create_order_partner(cr, uid, magento_app, sale_shop, values, context)

        """Partner Address Invoice OpenERP"""
        partner_address_invoice_id = self.magento_create_order_billing_address(cr, uid, magento_app, sale_shop, partner_id, customer_id, values, customer_info, context)

        """Partner Address Delivery OpenERP"""
        if values['shipping_address']:
            partner_address_shipping_id = self.magento_create_order_shipping_address(cr, uid, magento_app, sale_shop, partner_id, customer_id, values, customer_info, context)
        else:
            partner_address_shipping_id = partner_address_invoice_id

        """Reload Partner object"""
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context)

        """Payment Type"""
        if 'method' in values['payment']:
            payment_types = self.pool.get('magento.sale.shop.payment.type').search(cr, uid,
                    [('method','=',values['payment']['method']),('shop_id','=',sale_shop.id)]
                )
            if len(payment_types)>0:
                payment_type = self.pool.get('magento.sale.shop.payment.type').read(cr, uid, payment_types, ['payment_type_id'])
                vals['payment_type'] = payment_type[0]['payment_type_id'][0]

        """Sale Order"""
        if sale_shop.magento_reference:
            vals['name'] = values['increment_id']
        else:
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order')

        vals['magento_increment_id'] = values['increment_id']
        vals['shop_id'] = sale_shop.id
        vals['date_order'] = values['created_at'][:10]
        vals['partner_id'] = partner_id
        vals['partner_invoice_id'] = partner_address_invoice_id
        vals['partner_shipping_id'] = partner_address_shipping_id
        vals['partner_order_id'] = partner_address_invoice_id
        vals['pricelist_id'] = partner.property_product_pricelist.id
        vals['fiscal_position'] = partner.property_account_position.id
        if 'customer_note' in values:
            vals['note'] = values['customer_note']
        vals['origin'] = "%s-%s" % (magento_app.name,values['increment_id'])
        if 'gift_message' in values:
            vals['magento_gift_message'] = values['gift_message']

        vals['order_policy'] = sale_shop.magento_default_order_policy
        vals['picking_policy'] = sale_shop.magento_default_picking_policy
        vals['invoice_quantity'] = sale_shop.magento_default_invoice_quantity

        """Magento Status Order"""
        magento_status = values['status_history'][0]['status']
        vals['magento_status'] = magento_status
        mgn_status = self.pool.get('magento.sale.shop.status.type').search(cr, uid, [
                ('status','=',magento_status),
                ('shop_id','=',sale_shop.id),
            ])

        if len(mgn_status)>0:
            mgn_status = self.pool.get('magento.sale.shop.status.type').browse(cr, uid, mgn_status[0])
            vals['order_policy'] = mgn_status.order_policy
            vals['picking_policy'] = mgn_status.picking_policy
            vals['invoice_quantity'] = mgn_status.invoice_quantity
            if mgn_status.confirm:
                confirm = True
            if mgn_status.cancel:
                cancel = True
            if mgn_status.paidinweb:
                vals['magento_paidinweb'] = True

        """Magento Status history"""
        if 'status_history' in values:
            notes = []
            for history in values['status_history']:
                notes.append('%s - %s - %s' % (str(history['created_at']), str(history['status']), str(unicode(history['comment']).encode('utf-8'))) )
            vals['note'] = '\n'.join(notes)

        """Delivery Carrier"""
        if 'shipping_method' in values:
            delivery_ids = self.pool.get('delivery.carrier').search(cr, uid, [('code','=',values['shipping_method'])])
            if len(delivery_ids)>0:
                vals['carrier_id'] = delivery_ids[0]

        sale_order_id = self.create(cr, uid, vals, context)
        sale_order = self.browse(cr, uid, sale_order_id)

        """Sale Order Discount"""
        if values['discount_amount'] != '0.0000':
            sale_order_delivery = self.pool.get('sale.order.line').magento_create_discount_line(cr, uid, magento_app, sale_order, values, context)

        """Sale Order Delivery"""
        if 'shipping_method' in values:
            sale_order_delivery = self.pool.get('sale.order.line').magento_create_delivery_line(cr, uid, magento_app, sale_order, values, context)

        """Sale Order Line"""
        for item in values['items']:
            if item['product_type'] not in PRODUCT_TYPE_OUT_ORDER_LINE:
                sale_order_line = self.pool.get('sale.order.line').magento_create_order_line(cr, uid, magento_app, sale_order, item, context)

        """Add new order lines by mapping
        Mapping return dicc with price_unit and name
        Add default values line
        """
        mapping_order_lines = magento_app.mapping_sale_order_lines
        for mapping_order_line in mapping_order_lines:
            vals_line = self.pool.get('base.external.mapping').get_external_to_oerp(cr, uid, mapping_order_line.name, '', values, context)
            extra_line_name = vals_line.get('name', False)
            extra_line_price = vals_line.get('price_unit', False)
            if extra_line_name and extra_line_price:
                vals_line['order_id'] = sale_order.id
                vals_line['qty_ordered'] = 1
                vals_line['weight'] = 0
                vals_line['product_uom'] = magento_app.product_uom_id.id
                vals_line['purchase_price'] = vals_line['price_unit']
                self.pool.get('sale.order.line').create(cr, uid, vals_line, context)

        """Confirm Order - Change status sale order"""
        if confirm:
            LOGGER.notifyChannel('Magento Sync Sale Order', netsvc.LOG_INFO, "Order %s change status: Done" % (sale_order_id))
            netsvc.LocalService("workflow").trg_validate(uid, 'sale.order', sale_order_id, 'order_confirm', cr)

        """Cancel Order - Change status sale order"""
        if cancel:
            LOGGER.notifyChannel('Magento Sync Sale Order', netsvc.LOG_INFO, "Order %s change status: Cancel" % (sale_order_id))
            netsvc.LocalService("workflow").trg_validate(uid, 'sale.order', sale_order_id, 'cancel', cr)

        """Magento APP Customer
        Add last store - history stores buy
        """
        self.pool.get('magento.app.customer').magento_last_store(cr, uid, magento_app, partner, values)

        """Mapping Sale Order"""
        magento_external_referential_obj.create_external_referential(cr, uid, magento_app, 'sale.order', sale_order.id, values['order_id'])

        LOGGER.notifyChannel('Magento Sync Sale Order', netsvc.LOG_INFO, "Order %s, magento %s, openerp id %s, magento id %s" % (values['increment_id'], magento_app.name, sale_order.id, values['order_id']))

        cr.commit()

        return sale_order.id
        
    def magento_create_order_partner(self, cr, uid, magento_app, sale_shop, values, context=None):
        """Create Magento Partner/Customer"""
        magento_external_referential_obj = self.pool.get('magento.external.referential')
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner.address')

        customer_id = values['customer_id'] is not None and values['customer_id'] or values['billing_address']['customer_id']

        partner_mapping_id = magento_external_referential_obj.check_mgn2oerp(cr, uid, magento_app, 'res.partner', customer_id)
        if not partner_mapping_id and customer_id:
            customer_info = False
            customer  = partner_obj.magento_customer_info(magento_app, customer_id)

            #if partner exists (check same vat), not duplicity same partner
            partner_id = False
            partners = []
            if sale_shop.magento_check_vat_partner:
                #check if this customer are available by VAT
                if 'taxvat' in customer:
                    country_code = partner_address_obj.magento_get_customer_address_country_code(cr, uid, magento_app, customer, context)
                    vat = '%s%s' % (country_code, customer['taxvat'])
                    partners = partner_obj.search(cr, uid, [('vat','=',vat)])
                #check if this customer are available by email (magento.app.customer)
                partner_customers = self.pool.get('magento.app.customer').search(cr, uid, [('magento_emailid','=',customer['email'])])
                if len(partner_customers) > 0:
                    partner_customer = self.pool.get('magento.app.customer').browse(cr, uid, partner_customers[0])
                    partners.append(partner_customer.partner_id.id)

                if len(partners)>0:
                    partner_id = partners[0]
                    magento_external_referential_obj.create_external_referential(cr, uid, magento_app, 'res.partner', partner_id, customer['customer_id'])
                    LOGGER.notifyChannel('Magento Sync Partner', netsvc.LOG_INFO, "Create Mapping OpenERP: %s. Magento: %s" % (partner_id, customer['customer_id']))

            #create partner
            if not partner_id:
                partner_id = partner_obj.magento_create_partner(cr, uid, magento_app, customer, context)

            partner_mapping_id = magento_external_referential_obj.check_mgn2oerp(cr, uid, magento_app, 'res.partner', customer_id)

        if not customer_id:
            customer = values['billing_address']
            email = customer['email']
            mapping = False
            partner_customers = self.pool.get('magento.app.customer').search(cr, uid, [('magento_emailid','=',email)])
            if len(partner_customers) > 0:
                partner_customer = self.pool.get('magento.app.customer').browse(cr, uid, partner_customers[0])
                if partner_customer.magento_app_id.id != magento_app.id: #create new customer app
                    self.pool.get('magento.app.customer').magento_app_customer_create(cr, uid, magento_app, partner_id, customer, context)
                partner_id = partner_customer.partner_id.id
            else:
                customer['website_id'] = sale_shop.magento_website
                partner_id = partner_obj.magento_create_partner(cr, uid, magento_app, customer, mapping, context)
        else:
            partner_id = magento_external_referential_obj.get_external_referential(cr, uid, [partner_mapping_id])[0]['oerp_id']
            customer_id = magento_external_referential_obj.get_external_referential(cr, uid, [partner_mapping_id])[0]['mgn_id']

        return partner_id, customer_id

sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
        'magento_gift_message': fields.text('Gift Message'),
    }

    def magento_create_order_line(self, cr, uid, magento_app, sale_order, item={}, context=None):
        """
        Create Magento Order Line
        Not use Base External Mapping
        :magento_app: object
        :sale_order: object
        :item: dicc order line Magento
        :return sale_order_line_id (OpenERP ID)
        """
        magento_external_referential_obj = self.pool.get('magento.external.referential')

        decimals = self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price')
        
        #Default values
        product_id = False
        product_uom = magento_app.product_uom_id.id
        product_uom_qty = round(float(item['qty_ordered']),decimals)
        product_uos = product_uom
        product_uos_qty = product_uom_qty
        weight = item['weight'] and item['weight'] or 0
        weight = round(float(weight),decimals)

        products = []
        if magento_app.options and 'sku' in item:
            """Split SKU item (order line) by -
            Use Magneto ID in products (not Product ID OpenERP)"""
            skus = item['sku'].split('-') #order line magento, we get all products join by -
            if len(skus)>0:
                for sku in skus:
                    product = self.pool.get('product.product').search(cr, uid, [('magento_sku','=',sku)])
                    if len(product)>0:
                        product_mapping_id = magento_external_referential_obj.check_oerp2mgn(cr, uid, magento_app, 'product.product', product[0])
                        if product_mapping_id:
                            mgn_id = magento_external_referential_obj.get_external_referential(cr, uid, [product_mapping_id])[0]['mgn_id']
                            products.append(mgn_id)
                        else:
                            products.append(item['product_id'])
                    else:
                        products.append(item['product_id'])
            else:
                products.append(item['product_id'])
        else:
            products.append(item['product_id'])

        first = True
        for prod in products:
            vals_line = {}
            if 'tax_id' in item:
                vals_line['tax_id'] = item['tax_id']
            product_name = item['name']

            product_mapping_id = magento_external_referential_obj.check_mgn2oerp(cr, uid, magento_app, 'product.product', prod)
            if product_mapping_id:
                """Product is mapping. Get Product OpenERP"""
                product_id = magento_external_referential_obj.get_external_referential(cr, uid, [product_mapping_id])[0]['oerp_id']
                product = self.pool.get('product.product').browse(cr, uid, product_id)
                product_uom = product.uos_id.id and product.uos_id.id or product.uom_id.id
                product_uos = product.uos_id.id and product.uos_id.id or product.uom_id.id

                product_id_change = self.pool.get('sale.order.line').product_id_change(cr, uid,
                    [sale_order.id], sale_order.partner_id.property_product_pricelist.id, product.id,
                    product_uom_qty, product_uom, partner_id=sale_order.partner_id.id, fiscal_position=sale_order.fiscal_position.id)

                product_name = product_id_change['value']['name']
                weight = product_id_change['value']['th_weight']
                vals_line['delay'] = product_id_change['value']['delay']
                vals_line['type'] = product_id_change['value']['type']
                tax_ids = [self.pool.get('account.tax').browse(cr, uid, t_id).id for t_id in product_id_change['value']['tax_id']]
                vals_line['tax_id'] = [(6, 0, tax_ids)]
                vals_line['purchase_price'] = product_id_change['value']['purchase_price']

            vals_line['name'] = product_name
            vals_line['order_id'] = sale_order.id
            vals_line['product_id'] = product_id
            vals_line['product_uom_qty'] = product_uom_qty
            vals_line['product_uom'] = product_uom
            vals_line['product_uos_qty'] = product_uos_qty
            vals_line['product_uos'] = product_uos
            vals_line['th_weight'] = weight

            if first: #only first loop add price
                print item
                vals_line['price_unit'] = float(item['base_price'])
                if 'gift_message' in item:
                    vals_line['magento_gift_message'] = item['gift_message']
                vals_line['notes'] = item['description']
                first = False
            
            sale_order_line_id = self.create(cr, uid, vals_line, context)

        return sale_order_line_id

    def magento_create_delivery_line(self, cr, uid, magento_app, sale_order, values=False, context=None):
        """
        Create Magento Order Line Delivery
        Not use Base External Mapping
        :magento_app: object
        :sale_order: object
        :item: dicc order Magento
        :return sale_order_line_id (OpenERP ID)
        """
        if not values:
            return False

        delivery_product = magento_app.product_delivery_default_id
        name = delivery_product.name

        delivery_ids = self.pool.get('delivery.carrier').search(cr, uid, [('code','=',values['shipping_method'])])
        if len(delivery_ids)>0:
            delivery = self.pool.get('delivery.carrier').browse(cr, uid, delivery_ids[0], context)
            delivery_product = delivery.product_id
            name = "%s - %s" % (delivery.name, delivery_product.name)

        vals_line = {
            'order_id': sale_order.id,
            'product_id': delivery_product.id,
            'qty_ordered': 1,
            'weight': delivery_product.weight and delivery_product.weight or 0,
            'name': name,
            'price_unit': values['base_shipping_amount'],
            'notes': values['shipping_description'],
            'product_uom': delivery_product.uom_id.id,
        }

        #ADD taxes from shipping product
        tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, sale_order.fiscal_position, delivery_product.taxes_id)
        vals_line['tax_id'] = [(6, 0, tax_ids)]

        sale_order_line_id = self.create(cr, uid, vals_line, context)

        return sale_order_line_id

    def magento_create_discount_line(self, cr, uid, magento_app, sale_order, values=False, context=None):
        """
        Create Magento Order Line Discount
        Not use Base External Mapping
        :magento_app: object
        :sale_order: object
        :values: dicc order Magento
        :return sale_order_line_id (OpenERP ID)
        """
        if not values:
            return False

        discount_product = magento_app.product_discount_default_id

        vals_line = {
            'order_id': sale_order.id,
            'product_id': discount_product.id,
            'qty_ordered': 1,
            'weight': discount_product.weight and discount_product.weight or 0,
            'name': discount_product.name,
            'price_unit': values['discount_amount'],
            'product_uom': discount_product.uom_id.id,
        }

        #ADD taxes from discount product
        tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, sale_order.fiscal_position, discount_product.taxes_id)
        vals_line['tax_id'] = [(6, 0, tax_ids)]
        
        sale_order_line_id = self.create(cr, uid, vals_line, context)

        return sale_order_line_id

sale_order_line()