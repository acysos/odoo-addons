# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#                       Daniel Pascal <daniel@acysos.com>
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

import werkzeug.urls
from werkzeug.exceptions import NotFound
from openerp.osv import osv
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
import random
import json
import operator

PPG = 15

NPages = 9

def splitnumber(str):
    if ('.' in str):
        num1 = str.split('.', 1)
        
        if ((num1[0].isnumeric()) and (num1[1].isnumeric())):
            result = int(num1[0]) + float(num1[1]) / (10 ** len(num1[1]))
        else:
            result = 0  
    
    else:
        if (',' in str):
            num2 = str.split(',', 1)
            
            if ((num2[0].isnumeric()) and (num2[1].isnumeric())):
                result = int(num2[0]) + float(num2[1]) / (10 ** len(num2[1])) 
            else:
                result = 0  
        else:
            if (str.isnumeric()):
                result = str 
            else:
                result = 0
    
        
    return result  
        

class top_view(http.Controller):
    
    @http.route(['/realstate/top/<model("real.state.top"):top>'], type='http', auth="public", website=True)
    def realstatetops(self, top, **post):
        
        
        uid = request.uid
        user = request.env['res.users'].with_context(active_test=False).search([('id', '=', uid)])
       
        company = user.company_id
        
        
        values = {
            'tops' : top,
            'companies' : company
            }        
        return request.website.render("website_real_state.tops_template", values)

    
    @http.route(['/realstate/search',
                 '/realstate/search/page/<int:page>'], type='http', auth="public", website=True)
    def searchtopslist(self, page=0, **post):
        
        url = "/realstate/search"
        values = self.searchtops(page, url, post)
        values['page'] = page
        return request.website.render("website_real_state.search_list", values)
    
    
    @http.route(['/realstate/searchmap',
                 '/realstate/searchmap/page/<int:page>'], type='http', auth="public", website=True)
    def searchtopsmap(self, page=0, **post):
        
        url = "/realstate/searchmap"
        values = self.searchtops(page, url, post)
        values['page'] = page
        return request.website.render("website_real_state.search_map", values)
        
    
    
    
    
    
    
    
    
    def searchtops(self, page=0, url="",  post={}): 
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
           
        domain = [('website_published', '=', True), ('available', '=', True)]
        uid = request.uid
        
        user = request.env['res.users'].with_context(active_test=False).search([('id', '=', uid)])
       
        company = user.company_id
        
        zones1 = request.env['real.state.zone'].search([('id', '>', 0)])
        
        cities = request.env['real.state.cities'].sudo().search([('id', '>', 0)])
        
        type1 = [('unlimited','unlimited'),
             ('flat','Flat'),
             ('shop','Shop'),
             ('premise','Premise'),
             ('chalet','Chalet'),
             ('house','Town House'),
             ('office','Office'),
             ('premise-office','Premise-Office'),
             ('industrial_unit','Industrial Unit'),
             ('hotel_industry','Hotel Industry'),
             ('parking','Parking'),
             ('box_room','Box room'),
             ('land','Land')]
        
        operations1 = [('sale','Sale'),
                   ('rent','Rent'),
                   ('sale_rent','Sale & Rent'),
                   ('rent_sale_option','Rent with sale option'),
                   ('transfer','Transfer')]
        
        
        cities_ids = {}
        pamp = {}
        
        cities1 = cities.mapped('city_id')
        
        
        for city in cities1:
            if 'Pamplona' in city.city:
                if not city.city in pamp:
                    pamp[city.city] = str(city.id)
                else:
                    pamp[city.city] += '-'+str(city.id)
            else:
                if not city.city in cities_ids:
                    cities_ids[city.city] = str(city.id)
                else:
                    cities_ids[city.city] += '-'+str(city.id)
        
        citieswithoutpamp = sorted(cities_ids.items(), key=operator.itemgetter(0))
        pampcity = sorted(pamp.items(), key=operator.itemgetter(0))
        
        orderedcities = pampcity + citieswithoutpamp
        
        
        
        
        operation_sel = 'operation'
        zone_sel = 'zone'
        city_sel = 'city'
        category_sel = 'category'
        reference_def = 'reference'
        salepricefrom_def = 0
        salepriceto_def = 0
        rentpricefrom_def = 0
        rentpriceto_def = 0
        areafrom_def = 0
        areato_def = 0
        
        
        
        try:
            if (post['zone'] != 'zone'):
                domain += [('zone', '=', int(post['zone']))]
                zone_sel = int(post['zone'])
                
            if (post['category'] != 'category'):
                domain += [('type', '=', post['category'])]
                category_sel = post['category']
                
            if (post['operations'] != 'operation'):
                domain += [('operation', '=', post['operations'])]
                operation_sel = post['operations']
            
            if (post['reference'] != 'reference'):
                domain += [('name', '=', post['reference'])]
                reference_def = post['reference']
                
            if (splitnumber(post['salepricefrom']) > 0):
                domain += [('sale_price', '>=', splitnumber(post['salepricefrom']))]
                salepricefrom_def = post['salepricefrom']
                
            if (splitnumber(post['salepriceto']) > 0):
                domain += [('sale_price', '<=', splitnumber(post['salepriceto']))]
                salepriceto_def = post['salepriceto']
                
            if (splitnumber(post['rentpricefrom']) > 0):
                domain += [('rent_price', '>=', float(post['rentpricefrom']))]
                rentpricefrom_def = post['rentpricefrom']
                
            if (splitnumber(post['rentpriceto']) > 0):
                domain += [('rent_price', '<=', splitnumber(post['rentpriceto']))]
                rentpriceto_def = post['rentpriceto']
                
            if (splitnumber(post['areafrom']) > 0):
                domain += [('m2', '>=', splitnumber(post['areafrom']))]
                areafrom_def = post['areafrom']
                
            if (splitnumber(post['areato']) > 0):
                domain += [('m2', '<=', splitnumber(post['areato']))]
                areato_def = post['areato']
                
            if (post['city'] != 'city'):
                prooftonumber = []
                proofforstring = str(post['city']).split('-')
                for index in range(len(proofforstring)):
                    prooftonumber.append(int(proofforstring[index]))
                    
                
                domain += [('city_id', 'in', prooftonumber)] 
                city_sel = post['city']   
                       
            
        
        except:
            print "error"
            
            
            
        print domain
        
        tops = pool.get('real.state.top')
        
        
        top_count = tops.search_count(cr, uid, domain, context=context)
        
        pager = request.website.pager(url=url, total=top_count, page=page, step=PPG, scope=7, url_args=post)
        
        top_ids = tops.search(cr, uid, domain, limit=PPG, offset=pager['offset'], context=context)
        topss = tops.browse(cr, uid, top_ids, context=context)
        
        values = {
            'top' : topss,
            'pager' : pager, 
            'zone' : zones1,
            'operations' : operations1,
            'type1' : type1,
            'cities' : orderedcities,
            'companies' : company,
            'topids': top_ids,
            'operation_sel':  operation_sel,
            'zone_sel': zone_sel,
            'city_sel' : city_sel,
            'category_sel' : category_sel,
            'reference_def' : reference_def,
            'salepricefrom_def': salepricefrom_def,
            'salepriceto_def': salepriceto_def,
            'rentpricefrom_def': rentpricefrom_def,
            'rentpriceto_def': rentpriceto_def,
            'areafrom_def': areafrom_def,
            'areato_def': areato_def,
            
            }
        return values
    
    
    @http.route(['/realstate/featured',
                 '/realstate/featured/page/<int:page>'], type='http', auth="public", website=True)
    def featuredtops(self, page=0, **post): 
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        domain = [('website_published', '=', True), ('available', '=', True), ('website_featured', '=', True)]
        
        uid = request.uid
        
        user = request.env['res.users'].with_context(active_test=False).search([('id', '=', uid)])
       
        company = user.company_id
        
        url = '/realstate/featured'
        
        tops = pool.get('real.state.top')
        
        
        top_count = tops.search_count(cr, uid, domain, context=context)
        
        pager = request.website.pager(url=url, total=top_count, page=page, step=NPages, scope=7)
        
        top_ids = tops.search(cr, uid, domain, limit=NPages, offset=pager['offset'], context=context)
        topss = tops.browse(cr, uid, top_ids, context=context)
        
        
        
        
        prueba = random.sample(topss, 6)
        
        
        values = {
            'top' : prueba,
            'companies' : company,
            'pager' : pager, 
            'tops' : topss
            }
        
        return request.website.render("website_real_state.featured_tops", values)
    
    
    @http.route(['/realstate/maptops'], type='json', auth="public", website=True)
    def maptops(self, topsids):
        lists = http.request.env['real.state.top'].sudo().search(([('id','in',topsids)])).read()
        return json.dumps(lists)
    
    
    
    
    
    
    
    

    