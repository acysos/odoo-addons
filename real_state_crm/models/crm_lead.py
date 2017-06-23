# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
#           Daniel Pascal <daniel@acysos.com>
# Copyright (C) 2015  Acysos S.L.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import logging


class crm_top_suggested(models.Model):
    _name = 'crm.top.suggested'

    name = fields.Many2one('real.state.top', 'Top', required=True)
    interested = fields.Boolean('Interested', default=False)
    crm_id = fields.Many2one('crm.lead', 'CRM Lead', required=True,
                                  ondelete='cascade')
    updated = fields.Boolean('Updated')
    write_date = fields.Datetime('Update Date', readonly=True)
    


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    TYPES = [('unlimited', 'unlimited'),
             ('flat', 'Flat'),
             ('shop', 'Shop'),
             ('premise', 'Premise'),
             ('chalet', 'Chalet'),
             ('house', 'Town House'),
             ('office', 'Office'),
             ('premise-office', 'Premise-Office'),
             ('industrial_unit', 'Industrial Unit'),
             ('hotel_industry', 'Hotel Industry'),
             ('parking', 'Parking'),
             ('box_room', 'Box room'),
             ('land', 'Land')]

    OPERATIONS = [('sale', 'Sale'),
                  ('rent', 'Rent'),
                  ('sale_rent', 'Sale & Rent'),
                  ('rent_sale_option', 'Rent with sale option'),
                  ('transfer', 'Transfer'),
                  ('valuation', 'Valuation')]
    
    AVAILABLE_STATES = [('draft', 'Draft'),
                        ('open', 'Open'),
                        ('cancel', 'Cancel'),
                        ('done', 'Done'),
                        ('pending', 'Pending'),]

    
    zone_ids = fields.Many2many('real.state.zone',
                             'crm_lead_real_state_zone_rel',
                             'crm_lead_id', 'real_state_zone_id',
                             'Zones')
    top_type = fields.Selection(TYPES, 'Type', select=True)
    operation = fields.Selection(OPERATIONS, 'Operation', select=True)
    state = fields.Selection(AVAILABLE_STATES, 'State', default='draft', 
                             size=16, readonly=True)
    sale_price = fields.Float('Sale Price')
    rent_price = fields.Float('Rent Price')
    m2 = fields.Float('M2')
    parking = fields.Integer('Parking')
    elevator = fields.Boolean('Elevator')
    top_suggested_ids = fields.One2many('crm.top.suggested', 'crm_id',
                                     'Tops Suggested')
    prepared = fields.Boolean('Prepared')
    

    '''
    def search_tops_suggested(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if type(ids) is int:
            ids = [ids]
        if type(ids) is long:
            ids = [ids]
        top_obj = self.pool.get('real.state.top')
        sug_obj = self.pool.get('crm.top.suggested')
        for crm_lead in self.browse(cr, uid, ids, context):
            if crm_lead.state in ['open', 'pending']:
                sug_ids = [sug.id for sug in crm_lead.top_suggested_ids]
                domain = []
                if crm_lead.zone_ids:
                    zones = []
                    for zone in crm_lead.zone_ids:
                        zones.append(zone.id)
                    domain.append(('zone', 'in', zones))
                if crm_lead.top_type:
                    domain.append(('type', '=', crm_lead.top_type))
                if crm_lead.parking > 0:
                    domain.append(('parking', '>=', crm_lead.parking))
                if crm_lead.elevator:
                    domain.append(('elevator', '=', True))
                if crm_lead.operation:
                    if crm_lead.operation in ['sale']:
                        domain.append(('operation', 'in', ['sale', 'sale_rent',
                                                           'rent_sale_option']
                                       ))
                    elif crm_lead.operation in ['rent']:
                        domain.append(('operation', 'in', ['rent', 'sale_rent',
                                                           'rent_sale_option']
                                       ))
                    elif crm_lead.operation in ['sale_rent']:
                        domain.append(('operation', 'in', ['sale', 'rent',
                                                           'sale_rent',
                                                           'rent_sale_option']
                                       ))
                    else:
                        domain.append(('operation', 'in',
                                       [crm_lead.operation]))
                if crm_lead.sale_price > 0:
                    domain.append(('sale_price', '<=', crm_lead.sale_price))
                if crm_lead.rent_price > 0:
                    domain.append(('rent_price', '<=', crm_lead.rent_price))
                if crm_lead.m2 > 0:
                    if crm_lead.top_type in ['flat']:
                        domain.append(('flat_usage_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['shop', 'industrial_unit',
                                               'hotel_industry', 'premise']:
                        domain.append(('ground_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['office', 'premise-office']:
                        domain.append(('office_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['chalet', 'house']:
                        domain.append(('chalet_usage_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['land']:
                        domain.append(('land_m2', '>=', crm_lead.m2))
                if crm_lead.prepared:
                    if crm_lead.top_type == 'industrial_unit':
                        domain.append(('industrial_prepared', '=', True))
                    elif crm_lead.top_type == 'shop':
                        domain.append(('shop_prepared', '=', True))
                domain.append(('available', '=', True))
                top_ids = top_obj.search(cr, uid, domain)
                vals = {}
                if top_ids:
                    send_mail = False
                    for top in top_obj.browse(cr, uid, top_ids, context):
                        exist = sug_obj.search(cr, uid,
                                               [('crm_id', '=', crm_lead.id),
                                                ('name', '=', top.id)])
                        if not exist:
                            vals = {'name': top.id, 'crm_id': crm_lead.id,
                                    'interested': False, 'updated': True}
                            sug_obj.create(cr, uid, vals, context)
                            self.write(cr, uid, [crm_lead.id],
                                       {'state': crm_lead.state})
                            send_mail = True
                        else:
                            if top.write_date >= crm_lead.write_date:
                                sug_obj.write(cr, uid, exist,
                                              {'interested': True,
                                               'updated': True})
                                self.write(cr, uid, [crm_lead.id],
                                           {'state': crm_lead.state})
                                send_mail = True
                            if len(sug_ids) > 0:
                                if exist[0] in sug_ids:
                                    sug_ids.remove(exist[0])
                    if context.get('cron') is True and send_mail is True:
                        vals['interested'] = True
                        user_obj = self.pool.get('res.users')
                        user = user_obj.browse(cr, uid, uid)
                        template = user.company_id.realstate_template
                        if not template.id:
                            logger = netsvc.Logger()
                            logger.notifyChannel(
                                _("CRM Lead Real State"),
                                netsvc.LOG_ERROR,
                                _("Not template configured. "
                                  "Configure your company template or"
                                  " disallow Scheduled Actions"))
                        else:
                            mail_obj = self.pool.get(
                                'poweremail.templates')
                            mail_obj.generate_mail(cr, uid,
                                                   template.id, [crm_lead.id])
                sug_obj.unlink(cr, uid, sug_ids, context)

        return True
    
        '''
    
    @api.multi
    def search_tops_suggested(self):
        print "H2"
        top_obj = self.env['real.state.top']
        sug_obj = self.env['crm.top.suggested']
        for crm_lead in self:
            if crm_lead.state in ['open', 'pending']:
                sug_ids = [sug.id for sug in crm_lead.top_suggested_ids]
                domain = []
                if crm_lead.zone_ids:
                    zones = []
                    for zone in crm_lead.zone_ids:
                        zones.append(zone.id)
                    domain.append(('zone', 'in', zones))
                if crm_lead.top_type:
                    domain.append(('type', '=', crm_lead.top_type))
                if crm_lead.parking > 0:
                    domain.append(('parking', '>=', crm_lead.parking))
                if crm_lead.elevator:
                    domain.append(('elevator', '=', True))
                if crm_lead.operation:
                    if crm_lead.operation in ['sale']:
                        domain.append(('operation', 'in', ['sale', 'sale_rent',
                                                           'rent_sale_option']
                                       ))
                    elif crm_lead.operation in ['rent']:
                        domain.append(('operation', 'in', ['rent', 'sale_rent',
                                                           'rent_sale_option']
                                       ))
                    elif crm_lead.operation in ['sale_rent']:
                        domain.append(('operation', 'in', ['sale', 'rent',
                                                           'sale_rent',
                                                           'rent_sale_option']
                                       ))
                    else:
                        domain.append(('operation', 'in',
                                       [crm_lead.operation]))
                if crm_lead.sale_price > 0:
                    domain.append(('sale_price', '<=', crm_lead.sale_price))
                if crm_lead.rent_price > 0:
                    domain.append(('rent_price', '<=', crm_lead.rent_price))
                if crm_lead.m2 > 0:
                    if crm_lead.top_type in ['flat']:
                        domain.append(('flat_usage_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['shop', 'industrial_unit',
                                               'hotel_industry', 'premise']:
                        domain.append(('ground_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['office', 'premise-office']:
                        domain.append(('office_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['chalet', 'house']:
                        domain.append(('chalet_usage_m2', '>=', crm_lead.m2))
                    elif crm_lead.top_type in ['land']:
                        domain.append(('land_m2', '>=', crm_lead.m2))
                if crm_lead.prepared:
                    if crm_lead.top_type == 'industrial_unit':
                        domain.append(('industrial_prepared', '=', True))
                    elif crm_lead.top_type == 'shop':
                        domain.append(('shop_prepared', '=', True))
                domain.append(('available', '=', True))
                top_ids = top_obj.search(domain)
                vals = {}
                if top_ids:
                    send_mail = False
                    for top in top_ids:
                        exist = sug_obj.search([('crm_id', '=', crm_lead.id),
                                                ('name', '=', top.id)])
                        if not exist:
                            vals = {'name': top.id, 'crm_id': crm_lead.id,
                                    'interested': False, 'updated': True}
                            sug = sug_obj.create(vals)
                            sug.write({'state': crm_lead.state})
                            send_mail = True
                        else:
                            if top.write_date >= crm_lead.write_date:
                                sug_obj.write(exist,
                                              {'interested': True,
                                               'updated': True})
                                self.write([crm_lead.id],
                                           {'state': crm_lead.state})
                                send_mail = True
                            if len(sug_ids) > 0:
                                if exist[0] in sug_ids:
                                    sug_ids.remove(exist[0])
                    '''
                    if self.env.context.get('cron') is True and send_mail is True:
                        vals['interested'] = True
                        user  = self.env.user
                        template = user.company_id.realstate_template
                        if not template.id:
                            _logger = logging.getLogger(__name__)
                            _logger.debug('Not template configured. Configure your company template or disallow Scheduled Actions')
                        else:
                            mail_obj = self.env['email.templates']
                            mail_obj.generate_mail(template.id, [crm_lead.id])
                    '''
#               sug_obj.unlink(sug_ids)
        return True
    
    @api.multi
    def run_search_top_suggested(self):
        ids = self.search([('state', 'in', ['open', 'pending'])])
        context = self._context.copy()
        context['cron']= True
        sug_obj = self.env['crm.top.suggested']
        sug_true_ids = sug_obj.search([('updated', '=', True)])
        sug_true_ids.write({'updated': False})
        self.with_context(context).search_tops_suggested()
        return True


    @api.multi
    def write(self, vals):
        res = super(crm_lead, self).write(vals)
        print res
        print self
        if not self.env.context.get('cron'):
            self.search_tops_suggested()
        return res
        
    @api.model
    def create(self, vals):
        res_id = super(crm_lead, self).create(vals)
        print res_id
        res_id.search_tops_suggested()
        return res_id
    
    @api.multi
    def change_statep(self):
        self.ensure_one()
        self.state = self._context['state']
    
    
    
    
    
    
    
    
