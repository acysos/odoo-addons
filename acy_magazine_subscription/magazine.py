# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Based in internetdomain module.
#                       Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import osv, fields
from tools.translate import _
from tools import config

import time
import datetime
import netsvc

class magazine_magazine(osv.osv):
    
    def _last_number_get(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            cr.execute("select max(number) as last_number from magazine_published where magazine_id=%s", (rec.id,))
            res = cr.dictfetchone()
            result[rec.id] = res and res['last_number'] or False
        return result
    
    _name = 'magazine.magazine'
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'date_create': fields.date('Date', required=True),
        'last_number': fields.function(_last_number_get, method=True, type='integer', string='Last number published'),
        #'last_number': fields.integer('Last number published'),
        'magazines_published': fields.one2many('magazine.published','magazine_id', string='Magazines Published'),
    }
magazine_magazine()

class magazine_published(osv.osv):
    _name = 'magazine.published'
    _columns = {
        'date_publish': fields.date('Published', required=True),
        'number': fields.integer('Number', required=True),
        'magazine_id': fields.many2one('magazine.magazine','Magazine', required=True),
        'comments': fields.text('Comments'),
        'file': fields.binary('File'),
    }
    _defaults = {
        'date_publish': lambda *a: time.strftime('%Y-%m-%d'),
    }
magazine_published()

class magazine_subscription(osv.osv):
    
    def _number_expire_get(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            cr.execute("select max(last_number) as last_number from magazine_renewal where subscription_id=%s", (rec.id,))
            res = cr.dictfetchone()
            result[rec.id] = res and res['last_number'] or 0
        return result
        
    def _warning_expire(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = False

            magazine_alert_expire = rec.company_id.magazine_alert_expire
            if not magazine_alert_expire:
                max_alert = int(rec.magazine_id.last_number) + 5 # 5 number
            else:
                magazine_alert_expire = magazine_alert_expire.split(',')
                magazine_alert_expire = [int(x) for x in magazine_alert_expire]
                number_alert = magazine_alert_expire[0]
                for x in magazine_alert_expire:
                    if x > number_alert:
                        number_alert = x
                max_alert = int(rec.magazine_id.last_number) + number_alert
            if rec.expire_number != '0':
                expire_number = int(rec.expire_number)
                if expire_number <= max_alert:
                    result[rec.id] = True
            else:
                result[rec.id] = False
        return result
    
    #def run_mail_scheduler(self, cr, uid, use_new_cursor=False, context=None):
        #company_ids = self.pool.get('res.company').search(cr, uid, [])
        #for company_id in company_ids:
            #company = self.pool.get('res.company').browse(cr, uid, company_id)
            #magazine_alert_expire = company.magazine_alert_expire
            #if not magazine_alert_expire:
                #numbers_alert = [1] #1 magazine
            #else:
                #numbers_alert = magazine_alert_expire.split(',')
                #numbers_alert = [int(x) for x in days_alert]
            #for number in number_alert:
                #cr.execute("select domain_id from internetdomain_renewal as a LEFT JOIN internetdomain_domain AS b ON b.id = a.domain_id where a.date_expire=%s AND b.company_id = %s AND b.active = True", (datetime.date.today()+datetime.timedelta(days=day),company_id))
                #res = cr.dictfetchall()
                #ids = [r['domain_id'] for r in res]
                #for domain in self.browse(cr, uid, ids, context):
                    #template = domain.company_id.magazine_template
                    #logger = netsvc.Logger()
                    #if not template.id:
                        #logger.notifyChannel(_("Subscription"), netsvc.LOG_ERROR, _("Not template configurated. Configure your company template or desactive Scheduled Actions"))
                        #return False
                    #else:
                        #logger.notifyChannel(_("Subscription"), netsvc.LOG_INFO, _("Send email subcription: %s") % subscription.name)
                        #self.pool.get('poweremail.templates').generate_mail(cr, uid, template.id, [domain.id])
        #return True
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = False
        contact_addr_id = False

        if partner_id:
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'default'])
            contact_addr_id = res['default']

        result = {'value': {
            'partner_address_id': contact_addr_id,
            }
        }
        return result
    
    _name = 'magazine.subscription'
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'date_create': fields.date('Date', required=True),
        'warning_expire': fields.function(_warning_expire, method=True, type='boolean', string='Warning expired'),
        'first_number': fields.integer('First number'),
        'expire_number': fields.function(_number_expire_get, method=True, type='integer', string='Number expired'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'partner_address_id': fields.many2one('res.partner.address', 'Partner Contact', domain="[('partner_id','=',partner_id)]", required=True),
        'magazine_id': fields.many2one('magazine.magazine', 'Magazine', required=True),
        'comments': fields.text('Comments'),
        'active': fields.boolean('Active'),
        'renewal_ids': fields.one2many('magazine.renewal', 'subscription_id', string='Renewals'),
        #'product_ids': fields.many2many('product.product','magazine_product_rel','subscription_id','product_id','Products'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    
    def _default_company(self, cr, uid, context={}):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]

    _defaults = {
        'active': lambda *a: 1,
        'company_id': _default_company,
    }
    
magazine_subscription()


class magazine_renewal(osv.osv):
    
    _name = "magazine.renewal"
    _description = "Renewals"
    _columns = {
        'subscription_id': fields.many2one('magazine.subscription','Subscription', required=True, ondelete='cascade'),
        'date_renewal': fields.date('Date', required=True),
        'first_number': fields.integer('First number'),
        'last_number': fields.integer('Last number'),
        'price_unit': fields.float('Unit Price', required=True),
        'comments': fields.text('Comments'),
    }
    _defaults = {
        'date_renewal': lambda *a: time.strftime('%Y-%m-%d'),
    }

magazine_renewal()