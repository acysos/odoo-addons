# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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
import vatnumber

from magento import *

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def magento_create_partner(self, cr, uid, magento_app, values, mapping = True, context = None):
        """Create Partner from Magento Values
        Transform dicc by Base External Mapping
        :return partner_id
        """
        if context is None:
            context = {}

        vat = False
        vat_ok = False
        magento_vat = False
        if 'taxvat' in values:
            magento_vat = values['taxvat']

        logger = netsvc.Logger()

        external_referential_obj = self.pool.get('magento.external.referential')
        res_partner_vals_obj = self.pool.get('base.external.mapping')
        sale_shop_obj = self.pool.get('sale.shop')
        partner_address_obj = self.pool.get('res.partner.address')
        sale_shop_id = sale_shop_obj.search(cr,uid,[('magento_website','=',int(values['website_id']))],context=context)
        sale_shop = sale_shop_obj.browse(cr,uid,sale_shop_id[0],context=context)
        european_countries = ['at','be','bg','cy','cz','de','dk','ee','el','es','fi','fr','gb','hu','ie','it','lt','lu','lv','mt','nl','pl','pt','ro','se','si','sk']
        fiscal_position = sale_shop.non_vat_fiscal_position.id or None
        
        if magento_vat:
            country_obj = self.pool.get('res.country')
            country_code_search = magento_vat[:2]
            if country_code_search == 'EL': country_code_search = 'GR' #Fix Greece tax code
            country_id = country_obj.search(cr, uid, [('code', 'ilike', country_code_search)], context = context)
            
            if len(country_id) == 0: # The VAT has not a valid country code
                country_code = partner_address_obj.magento_get_customer_address_country_code(cr, uid, magento_app, values, context)
                if country_code == 'GR': country_code = 'EL' #Fix Greece tax code
                vat = '%s%s' % (country_code, magento_vat)
            else: # The VAT has a valid country code
                vat = magento_vat
            print vat
            if hasattr(self, 'check_vat_' + vat[:2].lower()):
                check = getattr(self, 'check_vat_' + vat[:2].lower())
                vat_ok = check(vat[2:])
            
            if vat_ok:
                values['vat'] = vat.upper()
                """If already exist a partner with the same VAT:
                Create External Referential
                Return partner_id
                """
                partner_id = self.search(cr, uid, [('vat', '=', values['vat'] )], context = context)
                if len(partner_id) > 0:
                    external_referential_obj.create_external_referential(cr, uid, magento_app, 'res.partner', partner_id[0], values['customer_id'])
                    return partner_id[0]

            if vat[:2].lower() == sale_shop.company_id.partner_id.vat[:2].lower():
                fiscal_position = sale_shop.national_fiscal_position.id or None
            elif vat[:2].lower() in european_countries:
                if vatnumber.check_vies(vat):
                    fiscal_position = sale_shop.valid_vies_fiscal_position.id or None
                else:
                    fiscal_position = sale_shop.non_valid_vies_fiscal_position.id or None
            else:
                fiscal_position = sale_shop.non_european_fiscal_position.id or None
                    
        else:
            print values
            if 'country_id' in values:
                country_code = values['country_id']
            else:
                country_code = partner_address_obj.magento_get_customer_address_country_code(cr, uid, magento_app, values, context)
            if country_code == 'GR': country_code = 'EL' #Fix Greece tax code
            print country_code
            if country_code.lower() in european_countries:
                fiscal_position = sale_shop.non_vat_fiscal_position.id or None
            else: 
                fiscal_position = sale_shop.non_european_fiscal_position.id or None

        context['magento_app'] = magento_app
        values['name'] = '%s %s' % (values['firstname'].capitalize(), values['lastname'].capitalize())
        res_partner_vals = res_partner_vals_obj.get_external_to_oerp(cr, uid, 'magento.res.partner', False, values, context)
        res_partner_vals['customer'] = True #fix this partner is customer
        res_partner_vals['property_account_position'] = fiscal_position
        partner_id = self.create(cr, uid, res_partner_vals, context)

        if mapping and ('customer_id' in values):
            external_referential_obj.create_external_referential(cr, uid, magento_app, 'res.partner', partner_id, values['customer_id'])
            self.pool.get('magento.log').create_log(cr, uid, magento_app, 'res.partner', partner_id, values['customer_id'], 'done', _('Successfully create partner: %s') % (values['name']) )
        else:
            self.pool.get('magento.log').create_log(cr, uid, magento_app, 'res.partner', partner_id, '', 'done', _('Successfully create partner: %s') % (values['name']) )
        if values.get('group_id', magento_app.customer_default_group.id):
            magento_app_customer_ids = self.pool.get('magento.app.customer').magento_app_customer_create(cr, uid, magento_app, partner_id, values, context)

        logger.notifyChannel('Magento Sync Partner', netsvc.LOG_INFO, "Create Partner: magento %s, openerp id %s, magento id %s" % (magento_app.name, partner_id, values['customer_id']))

        return partner_id
    
res_partner()