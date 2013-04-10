# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import magerp_osv
from base_external_referentials import external_osv

import tools
from tools.translate import _

import netsvc
import os

DEBUG = True
TIMEOUT = 2


class external_referential(magerp_osv.magerp_osv):
    _inherit = "external.referential"
    
    def sync_partner(self, cr, uid, ids, context):
        instances = self.browse(cr, uid, ids, context)

        for inst in instances:
            attr_conn = self.external_connection(cr, uid, inst, DEBUG)
            result = []
            result_address = []

            list_customer = attr_conn.call('customer.list')

            for each in list_customer:
                customer_id = int(each['customer_id'])

                each_customer_info = attr_conn.call('customer.info', [customer_id])
                result.append(each_customer_info)

                each_customer_address_info = attr_conn.call('customer_address.list', [customer_id])
                if len(each_customer_address_info):
                    customer_address_info = each_customer_address_info[0]
                    customer_address_info['customer_id'] = customer_id
                    customer_address_info['email'] = each_customer_info['email']
                    result_address.append(customer_address_info)
                    print customer_address_info

            partner_ids = self.pool.get('res.partner').ext_import(cr, uid, result, inst.id, context={})
            if result_address:
                partner_address_ids = self.pool.get('res.partner.address').ext_import(cr, uid, result_address, inst.id, context={})
            partner_obj = self.pool.get('res.partner')
            partner_obj.check_vat_vies(cr,uid,partner_ids['create_ids'],context)
            partner_obj.check_vat_vies(cr,uid,partner_ids['write_ids'],context)
        return True
    
external_referential()