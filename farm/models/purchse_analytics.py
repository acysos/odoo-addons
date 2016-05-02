# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime, timedelta

DFORMAT = "%Y-%m-%d %H:%M:%S"


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    farm = fields.Many2one(comodel_name='stock.location', string='Farm',
                           domain=[('usage', '=', 'view')])
    start_date = fields.Datetime(string='Bill start day')
    end_date = fields.Datetime(string='Bill end date')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        super(PurchaseOrder, self).write(vals)
        if 'state' in vals:
            if vals['state'] == 'done':
                for line in self.order_line:
                    if line.farm:
                        start_date = \
                            datetime.strptime(line.start_date, DFORMAT).date()
                        end_date = datetime.strptime(
                            line.end_date, DFORMAT).date()
                        afected_animals = self.get_party_per_day(
                            start_date, end_date, line.farm)
                        num_days = (end_date - start_date).days+1
                        self.set_analytics(afected_animals, line, num_days)

    def get_farm(self, location):
        while(location.location_id.id != 1):
            location = location.location_id
        return location

    @api.model
    def get_party_per_day(self, start_date, end_date, farm):
        pass_days = (end_date-start_date).days
        if pass_days < 1 or not end_date or not start_date:
            raise Warning(
                _('the bill should have lower starting date '
                  'to the final'))
        ani_groups_obj = self.env['farm.animal.group'].with_context({}).search(
            [('id', '!=', False)])
        ani_obj = self.env['farm.animal'].with_context({}).search(
            [('id', '!=', False)])
        party_per_day = {}
        animal_per_day = {}
        current_day = end_date
        while current_day >= start_date:
            party_per_day[current_day] = []
            animal_per_day[current_day] = []
            current_day = current_day - timedelta(days=1)
        for party in ani_groups_obj:
            transition_location = []
            for loc in party.specie.lost_found_location:
                transition_location.append(loc.location.id)
            transition = self.env['farm.transformation.event'].with_context(
                {}).search([('animal_group', '=', party.id),
                            ('from_location.id', 'in', transition_location),
                            ('to_location.id', 'not in', transition_location)])
            if party.state == 'sold':
                sale_move = self.env['farm.move.event'].with_context(
                    {}).search([('animal_group', '=', party.id)])
                sale_day = datetime.strptime(
                    sale_move[-1].timestamp, DFORMAT).date()
                if len(transition) < 1:
                    transition_finish = datetime.strptime(party.arrival_date,
                                                      DFORMAT).date()
                else:
                    transition_finish = datetime.strptime(transition.timestamp,
                                                      DFORMAT).date()
                if (start_date - sale_day).days < 0 and party.farm == farm:
                    if end_date < sale_day:
                        current_day = end_date
                    else:
                        current_day = sale_day
                    control_date = self.get_control_date(party, start_date,
                                                         transition_finish)
                    self.add_party(
                        party_per_day, party, current_day, control_date)
                elif self.get_farm(party.initial_location) == farm and \
                        (transition_finish - start_date).days > 0:
                    control_date = self.get_control_date2(party, start_date)
                    if end_date < transition_finish:
                        current_day = end_date
                    else:
                        current_day = transition_finish
                    self.add_party(party_per_day, party, current_day,
                                   control_date)
            elif party.state == 'fatten':
                if len(transition) < 1:
                    transition_finish = datetime.strptime(party.arrival_date,
                                                      DFORMAT).date()
                else:
                    transition_finish = datetime.strptime(transition.timestamp,
                                                      DFORMAT).date()
                if party.farm == farm:
                    control_date = self.get_control_date(party, start_date,
                                                         transition_finish)
                    self.add_party(
                        party_per_day, party, end_date, control_date)
                elif self.get_farm(party.initial_location) == farm and \
                        (transition_finish - start_date).days > 0:
                    control_date = self.get_control_date2(party, start_date)
                    if end_date < transition_finish:
                        current_day = end_date
                    else:
                        current_day = transition_finish
                    self.add_party(party_per_day, party, current_day,
                                   control_date)
            else:
                if party.farm == farm:
                    control_date = self.get_control_date2(party, start_date)
                    self.add_party(
                        party_per_day, party, end_date, control_date)
        for animal in ani_obj:
            if animal.farm == farm:
                control_date = self.get_control_date2(animal, start_date)
                self.add_party(animal_per_day, animal, end_date, control_date)
        return [party_per_day, animal_per_day]

    def add_party(self, party_per_day, party, current_day, control_date):
        while current_day >= control_date:
            party_per_day[current_day].append(party)
            current_day = current_day - timedelta(days=1)

    def get_control_date(self, party, start_date, transition_finish):
        if (start_date - transition_finish).days < 1:
            return transition_finish
        else:
            return start_date

    def get_control_date2(self, party, start_date):
        arrival_date = datetime.strptime(party.arrival_date, '%Y-%m-%d').date()
        if (arrival_date - start_date).days < 0:
            return start_date
        else:
            return arrival_date

    def set_analytics(self, afected_animals, line, num_days):
        cost_per_day = (line.price_unit * line.product_qty)/num_days
        for d, partys in afected_animals[0].iteritems():
            num_animals = len(afected_animals[1][d])
            for party in partys:
                num_animals += party.quantity
            if num_animals == 0:
                cost_per_animal_day = 0
                cost_per_day = cost_per_day + (cost_per_day/num_days)
            else:
                cost_per_animal_day = cost_per_day / num_animals
            for party in partys:
                self.set_party_cost(party, d, cost_per_animal_day)
            for animal in afected_animals[1][d]:
                self.set_animal_cost(animal, d, cost_per_animal_day)
            num_days -= num_days-1

    @api.one
    def set_party_cost(self, party, date, cost_per_animal_day):
        company = self.env['res.company'].with_context({}).search([
            ('id', '=', party.farm.company_id.id)])
        journal = self.env['account.analytic.journal'].with_context(
            {}).search([('code', '=', 'PUR')])
        analytic_line_obj = self.env['account.analytic.line']
        analytic_line_obj.create({
            'name': self.name,
            'date': date,
            'amount': -(cost_per_animal_day * party.quantity),
            'unit_amount': party.quantity,
            'account_id': party.account.id,
            'general_account_id': company.feed_account.id,
            'journal_id': journal.id,
            })

    @api.one
    def set_animal_cost(self, animal, date, cost_per_animal_day):
        company = self.env['res.company'].with_context({}).search([
            ('id', '=', animal.farm.company_id.id)])
        journal = self.env['account.analytic.journal'].with_context(
            {}).search([('code', '=', 'PUR')])
        analytic_line_obj = self.env['account.analytic.line']
        analytic_line_obj.create({
            'name': self.name,
            'date': date,
            'amount': -cost_per_animal_day,
            'unit_amount': 1,
            'account_id': animal.account.id,
            'general_account_id': company.feed_account.id,
            'journal_id': journal.id,
            })
