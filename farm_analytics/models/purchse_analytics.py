# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, sql_db, _
from openerp.http import request
from openerp.exceptions import Warning
from datetime import datetime, timedelta
import thread
from docutils.nodes import transition
from __builtin__ import False

DFORMAT = "%Y-%m-%d %H:%M:%S"
DAFORTMAT = "%Y-%m-%d"


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    @api.depends('order_id.imputed')
    def _get_imputed(self):
        for res in self:
            if res.order_id.imputed:
                res.imputed = res.order_id.imputed

    @api.multi
    @api.depends('price_unit', 'product_qty')
    def _get_aux_price_subtotal(self):
        for res in self:
            if res.price_unit and res.product_qty:
                res.aux_price_subtotal = res.price_unit * res.product_qty

    farm = fields.Many2one(comodel_name='stock.location', string='Farm',
                           domain=[('usage', '=', 'view')])
    location_id = fields.Many2one(comodel_name='stock.location', string='Yard',
                                  domain=[('usage', '!=', 'view'),
                                          ('silo', '!=', True)])
    start_date = fields.Datetime(string='Bill start day')
    end_date = fields.Datetime(string='Bill end date')
    general_expense = fields.Boolean(string='General Expense', default=False)
    imputed = fields.Boolean(string='Inputed', compute='_get_imputed',
                             store=True)
    aux_price_subtotal = fields.Float(string='amount_untaxed',
                                      compute='_get_aux_price_subtotal',
                                      store=True)

    @api.multi
    def impute_purchase_order(self):
        for res in self:
            res.order_id.set_purchase_analitics()


class Purchase_analitic_remain(models.Model):
    _name = 'purchase.analitic.remain'

    farm = fields.Many2one(comodel_name='stock.location', string='Farm')
    quantity = fields.Float(string='amount')
    last_calc = fields.Date(string='last day unit calc')
    quantity_per_unit = fields.Float(string='quantity per unit')


class Purchase_analitic_amortization(models.Model):
    _name = 'purchase.analitic.amortization'

    purchase_line_id = fields.Many2one(string='purchase line',
                                       comodel_name="purchase.order.line")
    initial_cuantity = fields.Float(string="Initial cuantity")
    current_quantity = fields.Float(string="current cuantity")
    start_date = fields.Date(string="Initial date")
    last_amortiztion = fields.Date(string="last amortization")
    planed_amortizations = fields.Integer('Planed amortizations')
    maked_amortizations = fields.Integer(string="Maked amortizations",
                                         default=0)
    farm = fields.Many2one(string="farm", comodel_name="stock.location")

    @api.multi
    def action_do(self):
        for res in self:
            if res.last_amortization:
                self.amort(res, datetime.today(), 1)
            else:
                pass

    def amort(self, res, day, loops):
        for n in range(loops):
            qty = res.current_quantity/(
                res.planed_amortizations - res.maked_amortizations)
            res.current_quantity -= qty
            res.maked_amortizations += 1
            res.last_amostization = day
            start_date = self.get_date_start(day)
            end_date = self.get_date_end(day)
            if res.farm and res.farm.factory:
                productions = self.env['mrp.production'].search(
                    [('date_finished', '>=', start_date),
                     ('date_finished', '<', end_date)])
                moves = []
                afected_lots = []
                total_feed = 0
                for production in productions:
                    total_feed = total_feed + production.product_qty
                    for mov in production.move_created_ids2:
                        moves.append(mov)
                amount = qty
                cost_per_kg = amount/total_feed
                for mov in moves:
                    for quant in mov.quant_ids:
                        lot = quant.lot_id
                        if lot.id not in afected_lots:
                            afected_lots.append(lot.id)
                            lot.unit_cost = lot.unit_cost + cost_per_kg
                            self.set_afected_feed_events(lot, cost_per_kg, day)
            elif res.farm and res.farm.transport:
                pick_type_obj = self.env['stock.picking.type']
                int_pick_type = pick_type_obj.search([
                    ('code', '=', 'internal')])
                out_pick_type = pick_type_obj.search([
                    ('code', '=', 'outgoing')])
                int_pick_type_ids = []
                for pick_t in int_pick_type:
                    int_pick_type_ids.append(pick_t.id)
                out_pick_type_ids = []
                for pick_t in out_pick_type:
                    out_pick_type_ids.append(pick_t.id)
                picking_obj = self.env['stock.picking']
                internal_trasports = picking_obj.search([
                    ('picking_type_id', 'in', int_pick_type_ids),
                    ('date_done', '<=', end_date),
                    ('date_done', '>=', start_date)])
                out_trasports = picking_obj.search([
                    ('picking_type_id', 'in', out_pick_type_ids),
                    ('date_done', '<=', end_date),
                    ('date_done', '>=', start_date)])
                tot_rel_trans = 0
                dest_tras = {}
                for transport in internal_trasports:
                    dest_loc = transport.move_lines[0].location_dest_id
                    warehouse = dest_loc.get_farm_warehouse()
                    tot_rel_trans = tot_rel_trans + warehouse.radius
                    dest = transport.move_lines[0].location_dest_id
                    if dest in dest_tras.keys():
                        dest_tras[dest][0] += warehouse.radius
                    else:
                        dest_tras[dest] = [warehouse.radius, transport.date_done]
                for transport in out_trasports:
                    warehouse = transport.picking_type_id.warehouse_id
                    dest_loc = warehouse.view_location_id
                    tot_rel_trans = tot_rel_trans + warehouse.radius
                    if dest in dest_tras.keys():
                        dest_tras[dest][0] += warehouse.radius
                    else:
                        dest_tras[dest] = [warehouse.radius, transport.date_done]
                cost_per_transport = (qty)/tot_rel_trans
                self.set_internal_trasport(
                    dest_tras, cost_per_transport, res.purchase_line_id.product_id.id)
            else:
                afected_animals = self.get_party_per_day(
                                    start_date, end_date, res.farm,
                                    res.purchase_line_id.location_id)
                if len(afected_animals[0]) == 0 \
                        and len(afected_animals[1]) == 0:
                    analitic_remain_ob = \
                        self.env['purchase.analitic.remain']
                    if res.farm:
                        farm = res.farm
                    else:
                        farm = self.get_farm(res.purchase_line_id.location_id)
                    analitic_remain = \
                        analitic_remain_ob.search([
                            ('farm', '=', farm.id)])
                    amount = qty
                    if len(analitic_remain) == 0:
                        analitic_remain_ob.create({
                            'farm': farm.id,
                            'quantity': amount})
                    else:
                        analitic_remain.quantity = \
                            analitic_remain.quantity + amount
                else:
                    cost_per_day = num_days = (end_date - start_date) 
                    animals = {}
                    analitic_party = {}
                    for d, partys in afected_animals[0].iteritems():
                        remain = 0
                        num_animals = 0
                        num_animals = len(afected_animals[1][d])
                        for party in partys:
                            num_animals += party.quantity
                        if farm:
                            analitic_remain_ob = self.env['purchase.analitic.remain']
                            analitic_remain = analitic_remain_ob.search([
                                ('farm', '=', farm.id)])
                        if num_animals == 0:
                            cost_per_animal_day = 0
                            if len(analitic_remain) == 0:
                                analitic_remain_ob.create({
                                    'farm': farm.id,
                                    'quantity': cost_per_day})
                            else:
                                analitic_remain.quantity = analitic_remain.quantity\
                                    + cost_per_day
                        else:
                            if farm and len(analitic_remain) != 0:
                                remain = analitic_remain.quantity
                                analitic_remain.unlink()
                            cost_per_animal_day = (cost_per_day + remain) / num_animals
                        if cost_per_animal_day != 0:
                            for party in partys:
                                if party in analitic_party.keys():
                                    analitic_party[party][0] += cost_per_animal_day * party.quantity
                                else:
                                    analitic_party[party] = [
                                        cost_per_animal_day * party.quantity, d]
                                #self.set_party_cost(party, d, cost_per_animal_day, new_env)
                            for animal in afected_animals[1][d]:
                                if animal.id in animals:
                                    animals[animal.id][1] = \
                                        animals[animal.id][1] + cost_per_animal_day
                                else:
                                    animals[animal.id] = [animal, cost_per_animal_day, d]
                    print analitic_party
                    for key, party in analitic_party.iteritems():
                        if party[0] > 0:
                            self.set_party_cost(key, party, res.purchase_line.product_id.id)
                    for key in animals.iterkeys():
                        an = animals[key]
                        self.env['purchase.order'].set_animal_cost(an[0], an[2], an[1])

    def get_date_start(self, date):
        year = date.year
        month = date.month
        return datetime(year, month, 1)

    def get_date_end(self, date):
        year = date.year
        month = date.month + 1
        if month == 13:
            month = 1
        return datetime(year, month, 1) - timedelta(days=1)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    imputed = fields.Boolean(string='Imputed', default=False)

    @api.multi
    def wkf_approve_order(self):
        super(PurchaseOrder, self).wkf_approve_order()
        for res in self:
            for line in res.order_line:
                if line.start_date:
                    end_date = datetime.strptime(line.end_date, DFORMAT)
                    start_date = datetime.strptime(line.start_date, DFORMAT)
                    pass_days = (end_date - start_date).days
                    if pass_days < 1 or not end_date or not start_date:
                        raise Warning(
                            _('the bill should have lower starting date '
                              'to the final'))
                if line.general_expense:
                    raise Warning(
                        _("General expenses can't aprove"))
                if line.farm and line.location_id:
                    raise Warning(_('Choose farm or yard'))
        return True

    @api.multi
    def set_purchase_analitics(self):
        for res in self:
            if not res.imputed:
                res.imputed = True
                control = res.order_line[0].general_expense
                for line in res.order_line:
                    if line.start_date and line.end_date:
                        end_date = datetime.strptime(
                                line.end_date, DFORMAT).date()
                        if end_date >= datetime.today().date():
                            raise Warning(
                                _('Final date after current date'))
                        if control and res.state != 'done':
                            res.wkf_po_done()
                        if line.farm and line.farm.factory:
                            self.set_factory_cost(line)
                        else:
                            start_date = \
                                datetime.strptime(
                                    line.start_date, DFORMAT).date()
                            num_days = (end_date - start_date).days+1
                            if line.farm and line.farm.transport:
                                self.set_transport_cost(line)
                            elif line.farm or line.location_id:
                                afected_animals = self.get_party_per_day(
                                    start_date, end_date, line.farm,
                                    line.location_id)
                                if len(afected_animals[0]) == 0 \
                                        and len(afected_animals[1]) == 0:
                                    analitic_remain_ob = \
                                        self.env['purchase.analitic.remain']
                                    if line.farm:
                                        farm = line.farm
                                    else:
                                        farm = self.get_farm(line.location_id)
                                    analitic_remain = \
                                        analitic_remain_ob.search([
                                            ('farm', '=', farm.id)])
                                    amount = line.price_unit * line.product_qty
                                    if len(analitic_remain) == 0:
                                        analitic_remain_ob.create({
                                            'farm': farm.id,
                                            'quantity': amount})
                                    else:
                                        analitic_remain.quantity = \
                                            analitic_remain.quantity + amount
                                else:
                                    thread.start_new_thread(
                                        self.set_analytics, (
                                            afected_animals, line,
                                            num_days, line.farm))

    @api.multi
    def set_transport_cost(self, line):
        pick_type_obj = self.env['stock.picking.type']
        int_pick_type = pick_type_obj.search([
            ('code', '=', 'internal')])
        out_pick_type = pick_type_obj.search([
            ('code', '=', 'outgoing')])
        int_pick_type_ids = []
        for pick_t in int_pick_type:
            int_pick_type_ids.append(pick_t.id)
        out_pick_type_ids = []
        for pick_t in out_pick_type:
            out_pick_type_ids.append(pick_t.id)
        picking_obj = self.env['stock.picking']
        internal_trasports = picking_obj.search([
            ('picking_type_id', 'in', int_pick_type_ids),
            ('date_done', '<=', line.end_date),
            ('date_done', '>=', line.start_date)])
        out_trasports = picking_obj.search([
            ('picking_type_id', 'in', out_pick_type_ids),
            ('date_done', '<=', line.end_date),
            ('date_done', '>=', line.start_date)])
        tot_rel_trans = 0
        dest_tras = {}
        for transport in internal_trasports:
            dest_loc = transport.move_lines[0].location_dest_id
            warehouse = dest_loc.get_farm_warehouse()
            tot_rel_trans = tot_rel_trans + warehouse.radius
            dest = transport.move_lines[0].location_dest_id
            if dest in dest_tras.keys():
                dest_tras[dest][0] += warehouse.radius
            else:
                dest_tras[dest] = [warehouse.radius, transport.date_done]
        for transport in out_trasports:
            warehouse = transport.picking_type_id.warehouse_id
            dest_loc = warehouse.view_location_id
            tot_rel_trans = tot_rel_trans + warehouse.radius
            if dest in dest_tras.keys():
                dest_tras[dest][0] += warehouse.radius
            else:
                dest_tras[dest] = [warehouse.radius, transport.date_done]
        cost_per_transport = (line.price_unit * line.product_qty)/tot_rel_trans
        self.set_internal_trasport(
            dest_tras, cost_per_transport, line.product_id.id)

    @api.multi
    def set_internal_trasport(self, dest_tras, cost_per_trans, product_id):
        print 'set int trans'
        animal_obj = self.env['farm.animal']
        an_group_obj = self.env['farm.animal.group']
        for dest, rad in dest_tras.iteritems():
            dest_loc = dest
            if dest_loc.silo:
                if not dest_loc.locations_to_fed:
                    continue
                dest_loc = dest_loc.locations_to_fed[0].location
            warehouse = dest_loc.get_farm_warehouse()
            animals = animal_obj.search([
                ('location', '=', dest_loc.id)])
            groups = an_group_obj.search([
                ('location', '=', dest_loc.id),
                ('state', '!=', 'sold')])
            tot_animals = len(animals)
            for group in groups:
                tot_animals = tot_animals + group.quantity
            tot_cost = cost_per_trans * rad[0]
            if tot_animals == 0:
                tot_animals = 1
            cost_per_animal = tot_cost/tot_animals
            for animal in animals:
                self.set_animal_cost(animal, rad[1],
                                     cost_per_animal, self.env)
            for group in groups:
                party = [cost_per_animal * group.quantity, rad[1]]
                self.set_party_cost(group, party, product_id)

    def set_factory_cost_old(self, line):
        analitic_remain_ob = self.env['purchase.analitic.remain']
        analitic_remain = analitic_remain_ob.search([
                                    ('farm', '=', line.farm.id)])
        amount = self.get_unit_price(line) * line.product_qty
        if len(analitic_remain) == 0:
                                    analitic_remain_ob.create({
                                        'farm': line.farm.id,
                                        'quantity': amount})
        else:
            analitic_remain.quantity = \
                analitic_remain.quantity + amount

    def set_factory_cost(self, line):
        new_cr = sql_db.db_connect(
            self.env.cr.dbname).cursor()
        uid, context = \
            self.env.uid, self.env.context
        with api.Environment.manage():
            new_env = api.Environment(
                new_cr, uid, context)
            productions = new_env['mrp.production'].search(
                [('date_finished', '>=', line.start_date),
                 ('date_finished', '<', line.end_date)])
            moves = []
            afected_lots = []
            total_feed = 0
            for production in productions:
                total_feed = total_feed + production.product_qty
                for mov in production.move_created_ids2:
                    moves.append(mov)
            amount = self.get_unit_price(line, new_env) * line.product_qty
            cost_per_kg = amount/total_feed
            for mov in moves:
                for quant in mov.quant_ids:
                    lot = quant.lot_id
                    if lot.id not in afected_lots:
                        afected_lots.append(lot.id)
                        lot.unit_cost = lot.unit_cost + cost_per_kg
                        self.set_afected_feed_events(lot, cost_per_kg, line.start_date,
                                                     new_env)
            new_env.cr.commit()
            new_cr.close()
            return True
 
    def set_afected_feed_events(self, lot, cost_kg, date, new_env=False):
        if not new_env:
            new_env = self.env
        feed_events = new_env['farm.feed.event'].search(
            [('state', '=', 'validated'),
             ('feed_lot', '=', lot.id),
             ('animal_type', '=', 'group')])
        journal = new_env['account.analytic.journal'].with_context(
            {}).search([('code', '=', 'PUR')])
        analytic_line_obj = new_env['account.analytic.line']
        for event in feed_events:
            company = new_env['res.company'].with_context({}).search([
            ('id', '=', 1)])
            amount = event.feed_quantity * cost_kg
            analytic_line_obj.create({
                'name': 'mrp-cost-' + self.name,
                'date': date,
                'amount': -amount,
                'unit_amount': 1,
                'account_id': event.animal_group.account.id,
                'general_account_id': company.feed_account.id,
                'journal_id': journal.id,
                })

    def get_farm(self, location):
        while(location.location_id.id != 1):
            location = location.location_id
        return location

    @api.model
    def get_party_per_day(self, start_date, end_date, farm, location_id):
        pass_days = (end_date-start_date).days
        if pass_days < 1 or not end_date or not start_date:
            raise Warning(
                _('the bill should have lower starting date '
                  'to the final'))
        ani_groups_obj = self.env['farm.animal.group'].with_context({}).search(
            ['|', ('removal_date', '>', start_date), ('removal_date', '=', False)])
        if location_id:
            ani_obj = self.env['farm.animal'].with_context({}).search(
                ['|', ('farm', '=', farm.id), ('location', '=', location_id.id)])
        else:
            ani_obj = self.env['farm.animal'].with_context({}).search(
                [('farm', '=', farm.id)])
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
                                                          DAFORTMAT).date()
                else:
                    transition_finish = datetime.strptime(
                        transition[-1].timestamp, DFORMAT).date()
                if farm:
                    condition1 = party.farm == farm
                else:
                    condition1 = party.location == location_id
                if (start_date - sale_day).days < 0 and condition1:
                    if end_date < sale_day:
                        current_day = end_date
                    else:
                        current_day = sale_day
                    control_date = self.get_control_date(party, start_date,
                                                         transition_finish)
                    self.add_party(
                        party_per_day, party, current_day, control_date)
            if party.state == 'fatten':
                if farm:
                    condition1 = party.farm == farm
                    condition2 = self.get_farm(party.initial_location) == farm
                else:
                    condition1 = party.location == location_id
                    condition2 = party.initial_location == location_id
                if len(transition) < 1:
                    transition_finish = datetime.strptime(party.arrival_date,
                                                          "%Y-%m-%d").date()
                else:
                    t_f = None
                    for tran in transition:
                        if t_f is None or t_f < tran.timestamp:
                            t_f = tran.timestamp
                    transition_finish = datetime.strptime(t_f,
                                                          DFORMAT).date()
                if condition1:
                    control_date = self.get_control_date(party, start_date,
                                                         transition_finish)
                    self.add_party(
                        party_per_day, party, end_date, control_date)
                elif condition2 and \
                        (transition_finish - start_date).days > 0 and \
                        (transition_finish - end_date).days < 0:
                    control_date = self.get_control_date2(party, start_date)
                    if end_date < transition_finish:
                        current_day = end_date
                    else:
                        current_day = transition_finish
                    self.add_party(party_per_day, party, current_day,
                                   control_date)
            else:
                if farm:
                    condition = party.farm == farm
                else:
                    condition = party.location == location_id
                if condition:
                    control_date = self.get_control_date2(party, start_date)
                    self.add_party(
                        party_per_day, party, end_date, control_date)
        for animal in ani_obj:
            if farm:
                condition = animal.farm == farm
            else:
                condition = animal.location == location_id
            if condition:
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

    def set_analytics(self, afected_animals, line, num_days, farm):
        print 'set analitics'
        new_cr = sql_db.db_connect(
            self.env.cr.dbname).cursor()
        uid, context = \
            self.env.uid, self.env.context
        with api.Environment.manage():
            new_env = api.Environment(
                new_cr, uid, context)
            cost_per_day = (self.get_unit_price(line, new_env) * line.product_qty)/num_days
            animals = {}
            analitic_party = {}
            for d, partys in afected_animals[0].iteritems():
                remain = 0
                num_animals = 0
                num_animals = len(afected_animals[1][d])
                for party in partys:
                    num_animals += party.quantity
                if farm:
                    analitic_remain_ob = new_env['purchase.analitic.remain']
                    analitic_remain = analitic_remain_ob.search([
                        ('farm', '=', farm.id)])
                if num_animals == 0:
                    cost_per_animal_day = 0
                    if len(analitic_remain) == 0:
                        analitic_remain_ob.create({
                            'farm': farm.id,
                            'quantity': cost_per_day})
                    else:
                        analitic_remain.quantity = analitic_remain.quantity\
                            + cost_per_day
                else:
                    if farm and len(analitic_remain) != 0:
                        remain = analitic_remain.quantity
                        analitic_remain.unlink()
                    cost_per_animal_day = (cost_per_day + remain) / num_animals
                if cost_per_animal_day != 0:
                    for party in partys:
                        if party in analitic_party.keys():
                            analitic_party[party][0] += cost_per_animal_day * party.quantity
                        else:
                            analitic_party[party] = [
                                cost_per_animal_day * party.quantity, d]
                        #self.set_party_cost(party, d, cost_per_animal_day, new_env)
                    for animal in afected_animals[1][d]:
                        if animal.id in animals:
                            animals[animal.id][1] = \
                                animals[animal.id][1] + cost_per_animal_day
                        else:
                            animals[animal.id] = [animal, cost_per_animal_day, d]
            print analitic_party
            for key, party in analitic_party.iteritems():
                if party[0] > 0:
                    self.set_party_cost(key, party, line.product_id.id, new_env)
            for key in animals.iterkeys():
                an = animals[key]
                new_env['purchase.order'].set_animal_cost(an[0], an[2], an[1], new_env)
            num_days -= num_days-1
            new_env.cr.commit()
            new_cr.close()
            return True

    @api.one
    def set_party_cost(self, group, party, product_id, new_env=False):
        if party[0] > 0:
            if not new_env:
                new_env = self.env
            company = new_env['res.company'].with_context({}).search([
                ('id', '=', 1)])
            journal = new_env['account.analytic.journal'].with_context(
                {}).search([('code', '=', 'PUR')])
            analytic_line_obj = new_env['account.analytic.line']
            analytic_line_obj.create({
                 'name': self.name,
                 'date': party[1],
                 'amount': -party[0],
                 'unit_amount': 1,
                 'account_id': group.account.id,
                 'general_account_id': company.feed_account.id,
                 'journal_id': journal.id,
                 'product_id': product_id
                 })
#         analytic_line_obj.create({
#             'name': self.name,
#             'date': date,
#             'amount': -(cost_per_animal_day * party.quantity),
#             'unit_amount': party.quantity,
#             'account_id': party.account.id,
#             'general_account_id': company.feed_account.id,
#             'journal_id': journal.id,
#             })

    @api.one
    def set_animal_cost(self, animal, date, cost_per_animal_day ,new_env=False):
        print 'animal cost'
        if cost_per_animal_day > 0:
            if not new_env:
                new_env = self.env
            company = new_env['res.company'].with_context({}).search([
                ('id', '=', animal.farm.company_id.id)])
            journal = new_env['account.analytic.journal'].with_context(
                {}).search([('code', '=', 'PUR')])
            analytic_line_obj = new_env['account.analytic.line']
            analytic_line_obj.create({
                'name': self.name,
                'date': date,
                'amount': -cost_per_animal_day,
                'unit_amount': 1,
                'account_id': animal.account.id,
                'general_account_id': company.feed_account.id,
                'journal_id': journal.id,
                })

    @api.multi
    def get_unit_price(self, line, new_env):
        invoice_line = new_env['account.invoice.line'].search(
            [('purchase_line_id', '=', line.id)])
        if invoice_line:
            return invoice_line[0].price_unit
        else:
            return line.price_unit
