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

NPages = 12


def splitnumber(txt_number):
    if ('.' in txt_number):
        num1 = txt_number.split('.', 1)

        if ((num1[0].isnumeric()) and (num1[1].isnumeric())):
            result = int(num1[0]) + float(num1[1]) / (10 ** len(num1[1]))
        else:
            result = 0

    else:
        if (',' in txt_number):
            num2 = txt_number.split(',', 1)

            if ((num2[0].isnumeric()) and (num2[1].isnumeric())):
                result = int(num2[0]) + float(num2[1]) / (10 ** len(num2[1]))
            else:
                result = 0
        else:
            if (txt_number.isnumeric()):
                result = txt_number
            else:
                result = 0

    return int(result)


class TopView(http.Controller):

    @http.route(['/realestate/top/<model("real.estate.top"):top>'],
                type='http', auth="public", website=True)
    def realestatetops(self, top, **post):
        uid = request.uid
        user = request.env['res.users'].with_context(active_test=False).search(
            [('id', '=', uid)])
        company = user.company_id
        values = {
            'tops': top,
            'companies': company
            }
        return request.render("website_real_estate.tops_template", values)

    @http.route(['/realestate/search',
                 '/realestate/search/page/<int:page>'], type='http',
                auth="public", website=True, csrf=False)
    def searchtopslist(self, page=0, **post):

        url = "/realestate/search"
        values = self.searchtops(page, url, post)
        values['page'] = page
        return request.render("website_real_estate.search_list", values)

    @http.route(['/realestate/searchmap',
                 '/realestate/searchmap/page/<int:page>'], type='http',
                auth="public", website=True, csrf=False)
    def searchtopsmap(self, page=0, **post):
        url = "/realestate/searchmap"
        values = self.searchtops(page, url, post)
        values['page'] = page
        return request.render("website_real_estate.search_map", values)

    def _get_top_domain(self, post):
        domain = [('website_published', '=', True), ('available', '=', True)]

        zones_domain = [('id', '>', 0)]
        city_sel = 'city'
        if 'city' in post:
            if (post['city'] != 'city'):
                prooftonumber = []
                proofforstring = str(post['city']).split('-')
                for index in range(len(proofforstring)):
                    prooftonumber.append(int(proofforstring[index]))
                domain += [('city_id', 'in', prooftonumber)]
                city_sel = post['city']
                zones_domain = ['|',
                                ('city_id', 'in', prooftonumber),
                                ('city_id', '=', None)]

        zones1 = request.env['real.estate.zone'].search(zones_domain)

        if 'zone' in post:
            if (post['zone'] != 'zone'):
                domain += [('zone', '=', int(post['zone']))]
        if 'category' in post:
            if (post['category'] != 'category'):
                domain += [('type', '=', str(post['category']))]
        if 'subtype' in post:
            if (post['subtype'] != 'subtype'):
                domain += [('subtype', '=', splitnumber(post['subtype']) )]
        if 'operations' in post:
            if (post['operations'] != 'operation'):
                operations_domain = [str(post['operations'])]
                if post['operations'] in ['sale', 'rent']:
                    operations_domain.append('sale_rent')
                domain += [('operation', 'in', operations_domain)]
        if 'reference' in post:
            if (post['reference'] != 'Reference'):
                domain += [('name', '=', str(post['reference']))]
        if 'salepricefrom' in post:
            if (splitnumber(post['salepricefrom']) > 0):
                domain += [(
                    'sale_price', '>=', splitnumber(post['salepricefrom']))]
        if 'salepriceto' in post:
            if (splitnumber(post['salepriceto']) > 0):
                domain += [(
                    'sale_price', '<=', splitnumber(post['salepriceto']))]
        if 'rentpricefrom' in post:
            if (splitnumber(post['rentpricefrom']) > 0):
                domain += [('rent_price', '>=', float(post['rentpricefrom']))]
        if 'rentpriceto' in post:
            if (splitnumber(post['rentpriceto']) > 0):
                domain += [(
                    'rent_price', '<=', splitnumber(post['rentpriceto']))]
        if 'areafrom' in post:
            if (splitnumber(post['areafrom']) > 0):
                domain += [('m2', '>=', splitnumber(post['areafrom']))]
        if 'areato' in post:
            if (splitnumber(post['areato']) > 0):
                domain += [('m2', '<=', splitnumber(post['areato']))]
        if 'bed' in post:
            if (splitnumber(post['bed']) > 0):
                domain += [('bedrooms', '=', splitnumber(post['bed']))]
            if (splitnumber(post['bed']) >= 3):
                domain += [('bedrooms', '>=', splitnumber(post['bed']))]
        if 'bath' in post:
            if (splitnumber(post['bath']) > 0):
                domain += [('bathroom', '=', splitnumber(post['bath']))]
            if (splitnumber(post['bed']) >= 3):
                domain += [('bathroom', '>=', splitnumber(post['bath']))]
        if 'reducedprice' in post:
            if post['reducedprice'] == 'reducedprice':
                domain += [('reduced_price', '=', True)]
        if 'parking' in post:
            if post['parking'] == 'parking':
                domain += [('parking', '>', 0)]
        if 'elevator' in post:
            if post['elevator'] == 'elevator':
                domain += [('elevator', '=', True)]
        if 'heating' in post:
            if post['heating'] == 'heating':
                domain += [('heating', '=', True)]
        if 'airconditioning' in post:
            if post['airconditioning'] == 'airconditioning':
                domain += [('airconditioning', '=', True)]

        return domain, zones1

    def searchtops(self, page=0, url="",  post={}):
        cr, uid = request.cr, request.uid
        context, pool = request.context, request.registry
        
        uid = request.uid

        user = request.env['res.users'].with_context(active_test=False).search(
            [('id', '=', uid)])

        company = user.company_id

        cities = request.env['real.estate.cities'].sudo().search(
            [('id', '>', 0)])

        type1 = [('unlimited', 'unlimited'),
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

        operations1 = [('sale', 'Sale'),
                       ('rent', 'Rent'),
                       ('sale_rent', 'Sale & Rent'),
                       ('rent_sale_option', 'Rent with sale option'),
                       ('new_development', 'New development'),
                       ('transfer', 'Transfer')]

        cities_ids = {}
        cities1 = cities.mapped('city_id')
        for city in cities1:
            if city.city not in cities_ids:
                cities_ids[city.city] = str(city.id)
            else:
                cities_ids[city.city] += '-'+str(city.id)

        orderedcities = sorted(cities_ids.items(), key=operator.itemgetter(0))

        city_sel = 'city'
        operation_sel = 'operation'
        zone_sel = 'zone'
        category_sel = 'category'
        subtype_sel = 'subtype'
        reference_def = 'reference'
        salepricefrom_def = 0
        salepriceto_def = 0
        rentpricefrom_def = 0
        rentpriceto_def = 0
        areafrom_def = 0
        areato_def = 0
        bed = '0'
        bath = '0'
        reducedprice = 'not-checked'
        parking = 'not-checked'
        elevator = 'not-checked'
        heating = 'not-checked'
        airconditioning = 'not-checked'
        
        

        if 'city' in post:
            if (post['city'] != 'city'):
                city_sel = post['city']
        if 'zone' in post:
            if (post['zone'] != 'zone'):
                zone_sel = int(post['zone'])
        if 'category' in post:
            if (post['category'] != 'category'):
                category_sel = post['category']
        if 'subtype' in post:
            if (post['subtype'] != 'subtype'):
                subtype_sel = splitnumber(post['subtype'])
        if 'operations' in post:
            if (post['operations'] != 'operation'):
                operation_sel = post['operations']
        if 'reference' in post:
            if (post['reference'] != 'Reference'):
                reference_def = post['reference']
        if 'salepricefrom' in post:
            if (splitnumber(post['salepricefrom']) > 0):
                salepricefrom_def = post['salepricefrom']
        if 'salepriceto' in post:
            if (splitnumber(post['salepriceto']) > 0):
                salepriceto_def = post['salepriceto']
        if 'rentpricefrom' in post:
            if (splitnumber(post['rentpricefrom']) > 0):
                rentpricefrom_def = post['rentpricefrom']
        if 'rentpriceto' in post:
            if (splitnumber(post['rentpriceto']) > 0):
                rentpriceto_def = post['rentpriceto']
        if 'areafrom' in post:
            if (splitnumber(post['areafrom']) > 0):
                areafrom_def = post['areafrom']
        if 'areato' in post:
            if (splitnumber(post['areato']) > 0):
                areato_def = post['areato']
        if 'bed' in post:
            bed = post['bed']
        if 'bath' in post:
            bath = post['bath']
        if 'reducedprice' in post:
            if post['reducedprice'] == 'reducedprice':
                reducedprice = 'checked'
        if 'parking' in post:
            if post['parking'] == 'parking':
                parking = 'checked'
        if 'elevator' in post:
            if post['elevator'] == 'elevator':
                elevator = 'checked'
        if 'heating' in post:
            if post['heating'] == 'heating':
                heating = 'checked'
        if 'airconditioning' in post:
            if post['airconditioning'] == 'airconditioning':
                airconditioning = 'checked'

        top_obj = request.env['real.estate.top']
        domain, zones1 = self._get_top_domain(post)
        top_count = top_obj.search_count(domain)

        pager = request.website.pager(
            url=url, total=top_count, page=page, step=PPG, scope=7,
            url_args=post)
        top_ids_object = top_obj.search(domain, limit=NPages,
                                        offset=pager['offset'])
        tops_ids = set([v[0].id for v in top_ids_object])

        topss = top_obj.browse(tops_ids)

        listToMap = [[], [], [], [], [], [], [], []]

        for t in topss:
            if t.image_ids:
                image_id = t.image_ids[0].id
            else:
                image_id = False
            if t.longitude:
                if t.latitude:
                    listToMap[0].append(t.latitude)
                    listToMap[1].append(t.longitude)
                    listToMap[2].append(t.id)
                    listToMap[3].append(image_id)
                    listToMap[4].append(t.zone.name)
                    listToMap[5].append(t.address.replace(',', ';'))
                    listToMap[6].append(t.m2)
                    listToMap[7].append(t.name)

        url_base = str(request.env['ir.config_parameter'].get_param(
            'web.base.url', False))

        subtypes_domain = [('id', '>', 0)]
        subtypes = request.env['real.estate.subtype'].search(
            subtypes_domain)

        values = {
            'top': topss,
            'pager': pager,
            'zone': zones1,
            'listToMap': listToMap,
            'operations': operations1,
            'type1': type1,
            'cities': orderedcities,
            'companies': company,
            'topids': tops_ids,
            'operation_sel':  operation_sel,
            'zone_sel': zone_sel,
            'city_sel': city_sel,
            'category_sel': category_sel,
            'reference_def': reference_def,
            'salepricefrom_def': salepricefrom_def,
            'salepriceto_def': salepriceto_def,
            'rentpricefrom_def': rentpricefrom_def,
            'rentpriceto_def': rentpriceto_def,
            'areafrom_def': areafrom_def,
            'areato_def': areato_def,
            'url_bases': url_base,
            'subtypes': subtypes,
            'subtype_sel': subtype_sel,
            'bed': bed,
            'bath': bath,
            'reducedprice': reducedprice,
            'parking': parking,
            'elevator': elevator,
            'heating': heating,
            'airconditioning': airconditioning,
        }

        return values

    @http.route(['/realestate/featured',
                 '/realestate/featured/page/<int:page>'], type='http',
                auth="public", website=True)
    def featuredtops(self, page=0, **post):
        cr, uid = request.cr, request.uid
        context, pool = request.context, request.registry

        domain = [('website_published', '=', True), ('available', '=', True),
                  ('website_featured', '=', True)]

        uid = request.uid

        user = request.env['res.users'].with_context(active_test=False).search(
            [('id', '=', uid)])

        company = user.company_id

        url = '/realestate/featured'

        top_obj = request.env['real.estate.top']

        top_count = top_obj.search_count(domain)

        pager = request.website.pager(url=url, total=top_count, page=page,
                                      step=NPages, scope=7)

        top_ids_object = top_obj.search(domain, limit=NPages,
                                        offset=pager['offset'])
        tops_ids = set([v[0].id for v in top_ids_object])

        topss = top_obj.browse(tops_ids)
        if len(topss) < 6:
            random_length = len(topss)
        else:
            random_length = 6
        random_top = random.sample(topss, random_length)

        values = {
            'top': random_top,
            'companies': company,
            'pager': pager,
            'tops': topss
            }

        return request.render("website_real_estate.featured_tops", values)

    @http.route(['/realestate/maptops'], type='json', auth="public",
                website=True)
    def maptops(self, topsids):
        lists = http.request.env['real.estate.top'].sudo().search(
            ([('id', 'in', topsids)])).read()
        return json.dumps(lists)

    