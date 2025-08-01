# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2020  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import HTTPException
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime

class Websitefarm(CustomerPortal):

    def check_farm_portal_rules(self, user):
        if not user.employee_id:
            return request.redirect('/web/login')
        else:
            return False



    @http.route('/farm', type='http', auth="public", website=True)
    def farm_menu(self, page=0, **post):
        result = self.check_farm_portal_rules(request.env.user)
        if result:
            return result
        values = {}
        response = request.render("website_farm.website_farm_menu", values)
        return response

    @http.route('/farm/removal', type='http', auth='public', website=True)
    def farm_removal(self):
        result = self.check_farm_portal_rules(request.env.user)
        if result:
            return result
        reasons = request.env['farm.removal.reason'].search([('id', '>', 0)])
        
        values = {'employee_id': request.env.user.id, 'reasons': reasons}
        return request.render("website_farm.website_removal", values)

    @http.route('/farm/animal', type='http', auth="public", website=True)
    def website_animal(self):
        result = self.check_farm_portal_rules(request.env.user)
        if result:
            return result
        #farmer = request.env['farm.farmer'].search([('employee_id', '=', request.env.user.employee_id)])
        result = {'farms': []}
        farms = request.env['stock.warehouse'].sudo().search([('active', '=', True)])
        for farm in farms:

            animals = request.env['farm.animal'].search([('farm', '=', farm.lot_stock_id.location_id.id)])
            groups = request.env['farm.animal.group'].search(
                [('farm', '=', farm.lot_stock_id.location_id.id),
                 ('state', '!=', 'sold')])
            group_count = 0
            for group in groups:
                group_count += group.quantity
            result['farms'].append({
                'farm': farm,
                'animals': len(animals),
                'group_count': group_count,
            })
        print(result)
        response = request.render("website_farm.website_animal", result)
        return response


    @http.route('/farm/farrowing', type='http', auth="public", website=True)
    def website_farrowing(self):
        result = self.check_farm_portal_rules(request.env.user)
        if result:
            return result
        farrowings = request.env['farm.event.order'].search([('employee', '=', request.env.user.id)])
        farrowing_values = []
        for farrow in farrowings:
            quantity = 0
            for line in farrow.farrowing_events:
                quantity += line.live
            farrowing_values.append({
                'farrow': farrow,
                'quantity': quantity,
            })
        values = {'lines': farrowing_values}
        response = request.render("website_farm.website_farrowing", values)

        return response

    @http.route('/farm/farrowing/request', type='json', auth="user", website=True)
    def farrowing_request(self):
        result = self.check_farm_portal_rules(request.env.user)
        if result:
            return result
        order = request.env['farm.event.order'].search([('employee', '=', request.env.user.id), ('state', '=', 'draft')])
        if not order:
            farmer = request.env['farm.farmer'].search(
                [('employee_id', '=', request.env.user.employee_id.id)])
            order = request.env['farm.event.order'].create({
                'employee': request.env.user.id,
                'state': 'draft',
                'event_type': 'farrowing',
                'timestamp': datetime.now(),
                'animal_type': 'female',
                'farm': farmer.farm_ids[0].id,
                'specie': farmer.specie_ids[0].id,
            })
        farrows = []
        for far in order.farrowing_events:
            farrows.append({'tag': far.animal.tag.name, 'live': far.live})
        values = {'employee_id': request.env.user.employee_id, 'order': order.id, 'farrowings': farrows}
        #response = http.Response(template='website_farm.farrowing_request', qcontext=values)
        print(values)
        response = request.render("website_farm.farrowing_request", values)
        return response.render()
        #return request.env['ir.ui.view']._render_template("website_farm.farrowing_request", values)

    @http.route('/farm/search/animal', type='json', auth="user", website=True)
    def search_animal(self, farm_label):
        label = request.env['farm.tags'].search([('name', '=', farm_label)])
        if label:
            animal = request.env['farm.animal'].search([('tag', '=', label.id)])
            if animal:
                return {
                    'type': 'Madre',
                    'breed': animal.breed.name,
                    'farm': animal.farm.name,
                    'origin': animal.farm_origin,
                    'arrival_date': animal.arrival_date,
                    'last_farrowing': animal.get_last_farrowing_day(),
                }
            else:
                group = request.env['farm.animal.group'].search(
                    [('tags', 'in', [label.id]), ('state', '!=', 'sold')])
                if group:
                    return {
                        'type': 'Cordero',
                        'breed': group.breed.name,
                        'farm': group.farm.name,
                        'location': group.initial_location.name,
                        'arrival_date': group.arrival_date,
                        'mother': group.mother,
                        'origin': group.farm_origin,
                    }
                else:
                    return {'error': 'Animal not found'}
        else:
            return {'error': 'Label not found'}

    @http.route('/farm/next_farrowing', type='json', auth="user", website=True)
    def next_farrowing(self, farm_label, live, order, label1, label2, label3, label4, label5, sex1, sex2, sex3, sex4, sex5):
        female_label = request.env['farm.tags'].search([('name', '=', farm_label)])
        if female_label:
            female = request.env['farm.animal'].search([('tag', '=', female_label.id)])
        else:
            return {'error': 'Label not found'}
        if not female:
            return {'error': 'Animal not found'}
        order = request.env['farm.event.order'].browse(int(order))
        if not order.farrowing_events:
            order.farm = female.farm
        labels = []
        sex = []
        if label1:
            labels.append(label1)
            sex.append(sex1)
            if label2:
                labels.append(label2)
                sex.append(sex2)
                if label3:
                    labels.append(label3)
                    sex.append(sex3)
                    if label4:
                        labels.append(label4)
                        sex4.append(sex4)
                        if label5:
                            labels.append(label5)
                            sex.append(sex5)
        animal_labels = []
        for label in labels:
            animal_label = request.env['farm.tags'].sudo().search([('name', '=', label)])
            if animal_label:
                animal_labels.append(animal_label)
            else:
                animal_labels.append(request.env['farm.tags'].sudo().create({'name': label}))
        new_farrow = request.env['farm.farrowing.event'].sudo().create({
            'job_order': order.id,
            'live': live,
            'new_tags': [(6, 0, [x.id for x in animal_labels])],
            'animal_type': 'female',
            'farm': female.farm.id,
            'animal': female.id,
            'specie': female.specie.id,
            'timestamp': datetime.now(),
            'employee': request.env.user.id,
        })
        aux = 0
        for tag in sex:
            if tag == 'male':
                request.env['farm.tags.farrow.males'].sudo().create({
                    'tag': animal_labels[aux].id,
                    'farrow_id': new_farrow.id,
                })
            else:
                request.env['farm.tags.farrow.females'].sudo().create({
                    'tag': animal_labels[aux].id,
                    'farrow_id': new_farrow.id,
                })
            aux += 1
        return False

    @http.route('/farm/farrowing/submit', type='json', auth="user", website=True)
    def farrowing_submit(self, order):
        error = ''
        try:
            order = request.env['farm.event.order'].browse(int(order))
            order.confirm()
        except HTTPException as e:
            error = e.description
        response = request.render("website_farm.website_farrowing", {'error': error})
        return response.render()

    @http.route('/farm/removal/submit', type='json', auth="user", website=True)
    def removal_submit(self, employee_id, tag, reason):
        error = ''
        try:
            employee = request.env['hr.employee'].browse(int(employee_id))
            label = request.env['farm.tags'].search([('name', '=', tag)])
            if not label:
                raise HTTPException(description=_('Label not found'))
            animal = request.env['farm.animal'].search([('tag', '=', label.id)])
            target = 'animal'
            if not animal:
                animal = request.env['farm.animal.group'].search(
                    [('tags', 'in', [label.id]), ('state', '!=', 'sold')])
                animal_type = 'group'
                target = 'animal_group'
                if not animal:
                    raise HTTPException(description=_('Animal not found'))
            else:
                animal_type = animal.type

            vals = {
                'employee': employee.id,
                target: animal.id,
                'timestamp': datetime.now(),
                'animal_type': animal_type,
                'specie': animal.specie.id,
                'farm': animal.farm.id,
                'from_location': animal.location.id,
                'quantity': 1,
                'reason': int(reason),
            }
            if animal_type == 'group':
                vals['animal_group'] = animal.id
                vals['removed_tags'] = [(6, 0, [label.id])]
            else:
                vals['animal'] = animal.id
            removal = request.env['farm.removal.event'].create(vals)
            removal.confirm()

        except HTTPException as e:
            error = e.description
        if error:
            response = request.render("website_farm.website_removal", {'error': error})
            return response.render()
        else:
            print('redirecting')
            return request.redirect('/farm')