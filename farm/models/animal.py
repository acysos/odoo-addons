# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime

ANIMAL_ORIGIN = [('purchased', 'Purchased'),
                 ('raised', 'Raised'), ]
ANIMAL_TYPE = [('male', 'Male'), ('female', 'Female'),
               ('individual', 'Individual'), ]
DFORMAT = "%Y-%m-%d %H:%M:%S"


class Tag(models.Model):
    _name = 'farm.tags'

    name = fields.Char(string='Name', required=True)
    animals = fields.Many2many(
        comodel_name='farm.animal', inverse_name='tags',
        string='Animals')
    animal_group = fields.Many2many(
        comodel_name='farm.animal.group', inverse_name='tags',
        string='Groups')


class Animal(models.Model):
    _name = 'farm.animal'
    _rec_name = 'number'

    type = fields.Selection(selection=ANIMAL_TYPE, string='Type',
                            default='individual')
    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Specie', required=True, select=True)
    breed = fields.Many2one(comodel_name='farm.specie.breed', string='Breed',
                            required=True)
    tags = fields.Many2many(
        comodel_name='farm.tags', inverse_name='animals',
        string='Tags')
    lot = fields.One2many(comodel_name='stock.lot_farm.animal',
                          inverse_name='animal', colum1='lot',
                          string='lot')
    number = fields.Char(string='Number',
                         related='lot.lot.name')
    location = fields.Many2one(
        comodel_name='stock.location', string='Current Location',
        domain=[
            ('silo', '=', False),
            ], help='Indicates where the animal currently resides.')
    farm = fields.Many2one(comodel_name='stock.location',
                           domain=[('usage', '=', 'view'), ],
                           string='Current Farm')
    origin = fields.Selection(selection=ANIMAL_ORIGIN, string='Origin',
                              required=True)
    arrival_date = fields.Date(string='Arrival Date',
                               default=fields.Date.today(),
                               help="The date this animal arrived (if it"
                               "was purchased) or when it was born.")
    initial_location = fields.Many2one(
        comodel_name='stock.location', string='Initial Location',
        required=True,
        domain=[('usage', '=', 'internal'), ('silo', '=', False), ],
        help="The Location where the animal was reached or where it was "
        "allocated when it was purchased.\nIt is used as historical "
        "information and to get Serial Number.")
    birthdate = fields.Date(string='Birthdate', default=fields.Date.today())
    removal_date = fields.Date(
        string='Removal Date', readonly=True,
        defaulft=fields.Date.today(),
        help='Get information from the corresponding removal event.')
    removal_reason = fields.Many2one(comodel_name='farm.removal.reason',
                                     readonly=True)
    weight = fields.One2many(comodel_name='farm.animal.weight',
                             inverse_name='animal', string='Weigth records',)
    current_weight = fields.Many2one(comodel_name='farm.animal.weight',
                                     string='Current Weight',
                                     compute='get_current_weight')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    consumed_feed = fields.Float(string='Consumed Feed (kg)')
    sex = fields.Selection([('male', "Male"),
                            ('female', "Female"),
                            ('undetermined', "Undetermined"),
                            ], string='Sex', required=True)
    purpose = fields.Selection([('sale', 'Sale'),
                                ('replacement', 'Replacement'),
                                ('unknown', 'Unknown'),
                                ], string='Purpose', default='unknown')
    account = fields.Many2one(comodel_name='account.analytic.account',
                              string='Analytic Account')

    @api.multi
    def create_first_move(self, res):
        moves_obj = self.env['stock.move']
        quant_obj = self.env['stock.quant']
        for record in res:
            quant = quant_obj.search([(
                'lot_id', '=', record.lot.lot.id)])
            if record.origin == 'raised':
                if not quant:
                    raise_location = self.env['stock.location'].search(
                        [('usage', '=', 'production')])
                    product_tmpt = record.lot.lot.product_id.product_tmpl_id
                    new_move = moves_obj.create({
                        'origin': res.origin,
                        'name': 'raise-' + record.lot.lot.name,
                        'create_date': fields.Date.today(),
                        'date': record.arrival_date,
                        'product_id': record.lot.lot.product_id.id,
                        'product_uom_qty': 1,
                        'product_uom': product_tmpt.uom_id.id,
                        'location_id': raise_location.id,
                        'location_dest_id': record.initial_location.id,
                        'company_id': record.farm.company_id.id,
                        })
                    new_move.action_done()
                    new_move.quant_ids.lot_id = record.lot.lot.id
                else:
                    raise Warning(
                        _('this lot is in use, please create new lot'))
            elif len(self.lot) > 0:
                if not quant:
                    raise Warning(
                        _('no product in farms for this lot'))
                elif quant.location_id != record.initial_location:
                    raise Warning(
                        _('animal location and product location are diferent'))

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(Animal, self).create(vals)
        self.create_first_move(res)
        res.location = res.initial_location
        analy_ac_obj = self.env['account.analytic.account']
        new_account = analy_ac_obj.create({
            'name': 'AA-'+res.type+'-'+res.number})
        res.account = new_account
        tags_obj = self.env['farm.tags']
        new_tag = tags_obj.search([
            ('name', '=', res.farm.name + '-unmated')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': res.farm.name + '-unmated', })
        res.tags = [(6, 0, [new_tag.id, ])]
        return res

    @api.one
    def get_current_weight(self):
        if self.weight:
            self.current_weight = self.weight[0].id


class AnimalWeight(models.Model):
    _name = 'farm.animal.weight'
    _order = 'timestamp DESC'
    _rec_name = 'weight'

    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             required=True, ondelete='CASCADE')
    timestamp = fields.Datetime(string='Date & Time', required=True,
                                defaulft=fields.Date.today())
    uom = fields.Many2one(comodel_name='product.uom', string='Uom',
                          requiered=True, ondelete='CASCADE')
    weight = fields.Float(string='Weight', digits=(16, 2))


class Male(models.Model):
    _inherit = 'farm.animal'

    extractions = fields.One2many(comodel_name='farm.semen_extraction.event',
                                  inverse_name='animal',
                                  string='Semen Extractions')
    last_extraction = fields.Date(string='Last Extraction', readonly=True,
                                  compute='get_last_extraction')

    @api.one
    def get_last_extraction(self):
        if not self.extractions:
            return False
        extraction = self.extractions.search(
            [('animal', '=', self.id)],
            order='timestamp DESC')[0]
        self.last_extraction = extraction.timestamp


class Female(models.Model):
    _inherit = 'farm.animal'

    cycles = fields.One2many(comodel_name='farm.animal.female_cycle',
                             inverse_name='animal', string='Cycles)')
    current_cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                                    string='Current Cycle', readonly=True,
                                    compute='get_current_cycle')
    state = fields.Selection(selection=[('initial', ''),
                                        ('prospective', 'Prospective'),
                                        ('unmated', 'Unmated'),
                                        ('mated', 'Mated'),
                                        ('removed', 'Removed'), ],
                             readonly=True, default='prospective',
                             help='According to NPPC Production and Financial'
                             'Standards there are four status for breeding'
                             'sows The status change is event driven:arrival'
                             'date, entry date mating event and removal event')
    first_mating = fields.Date(string='First Mating',
                               compute='get_first_mating')
    days_from_insemination = fields.Integer(
        string='Insemination Days',
        compute='get_days_from_insemination')
    last_produced_group = fields.Many2one(comodel_name='farm.animal.group',
                                          string='Last produced group',
                                          compute='get_last_produced_group')
    days_from_farrowing = fields.Integer(string='Unpregnat Days',
                                         compute='get_days_from_farrowing')

    def is_lactating(self):
        return (self.current_cycle and
                self.current_cycle.state == 'lactating' or False)

    @api.multi
    def get_current_cycle(self):
        for res in self:
            if len(res.cycles) > 0:
                res.current_cycle = res.cycles[-1]

    @api.one
    def update_state(self):
        if self.type != 'female':
            self.state = 'initial'
        else:
            if self.removal_date and self.removal_date <= fields.Date.today():
                state = 'removed'
            elif (not self.cycles or len(self.cycles) == 1 and
                    not self.cycles[0].weaning_event and
                    self.cycles[0].state == 'unmated'):
                state = 'prospective'
            elif self.current_cycle and self.current_cycle.state == 'unmated':
                state = 'unmated'
            else:
                state = 'mated'
            self.state = state

    @api.one
    def get_first_mating(self):
        InseminationEvent = self.env['farm.insemination.event']
        if self.type != 'female':
            self.first_mating = False
        else:
            first_inseminations = InseminationEvent.search([
                ('animal', '=', self.id),
                ], limit=1, order='timestamp ASC')
            if not first_inseminations:
                self.first_mating = False
            else:
                first_insemination, = first_inseminations
                self.first_mating = first_insemination.timestamp

    @api.one
    def get_days_from_insemination(self):
        InseminationEvent = self.env['farm.insemination.event']
        last_valid_insemination = InseminationEvent.search([
            ('animal', '=', self.id),
            ('state', '=', 'validated'),
            ], order='timestamp DESC', limit=1)
        if not last_valid_insemination:
            self.days_from_insemination = False
        else:
            val_in = datetime.strptime(
                last_valid_insemination[0].timestamp, DFORMAT)
            days_from_insemination = (
                datetime.today() - val_in).days
            self.days_from_insemination = days_from_insemination

    @api.one
    def get_last_produced_group(self):
        FarrowingEvent = self.env['farm.farrowing.event']
        last_farrowing_events = FarrowingEvent.search([
            ('animal', '=', self.id),
            ('state', '=', 'validated'),
            ('produced_group', '!=', None),
            ], order='timestamp DESC', limit=1)
        if last_farrowing_events:
            self.last_produced_group = \
                last_farrowing_events[0].produced_group.id
        else:
            self.last_produced_group = False

    @api.one
    def get_days_from_farrowing(self):
        FarrowingEvent = self.env['farm.farrowing.event']
        last_valid_farrowing = FarrowingEvent.search([
            ('animal', '=', self.id),
            ('state', '=', 'validated'),
            ], order='timestamp DESC', limit=1)
        if not last_valid_farrowing:
            self.days_from_farrowing = False
        else:
            last_val_farrow = datetime.strptime(
                last_valid_farrowing[0].timestamp, DFORMAT)
            days_from_farrowing = (
                datetime.today() - last_val_farrow).days
            self.days_from_farrowing = days_from_farrowing


class FemaleCycle(models.Model):
    _name = 'farm.animal.female_cycle'
    _order = 'ordination_date ASC'
    _rec_name = 'sequence'

    animal = fields.Many2one(comodel_name='farm.animal', string='Female',
                             required=True, domain=['type', '=', 'female'])
    sequence = fields.Integer(string='Nun. cycle')
    ordination_date = fields.Datetime('Date for ordination', requiered=True,
                                      default=fields.Datetime.now())
    state = fields.Selection(selection=[
        ('mated', 'Mated'), ('pregnat', 'Pregnat'),
        ('lactating', 'Lactating'), ('unmated', 'Unmated')],
        readonly=True, required=True, default='unmated')
    insemination_events = fields.One2many(
        comodel_name='farm.insemination.event',
        inverse_name='female_cycle', string='Inseminations')
    days_between_wearing_and_insemination = fields.Integer(
        string='Unmated Days',
        compute='get_days_between_weaning_and_insemination')
    diagnosis_events = fields.One2many(
        comodel_name='farm.pregnancy_diagnosis.event',
        inverse_name='female_cycle', string='Diagnosis')
    pregnant = fields.Boolean(string='Pregnat',
                              compute='on_change_whith_pregnant')
    abort_event = fields.One2many(comodel_name='farm.abort.event',
                                  inverse_name='female_cycle',
                                  string='Abort')
    farrowing_event = fields.One2many(
        comodel_name='farm.farrowing.event_female_cycle',
        inverse_name='cycle', column1='female_cycle.event', string='Farrowing',
        readonly=True)
    live = fields.Integer(string='Live', compute='get_live')
    dead = fields.Integer(string='Dead', compute='get_dead')
    foster_events = fields.One2many(comodel_name='farm.foster.event',
                                    inverse_name='female_cycle',
                                    string='Fosters')
    fostered = fields.Integer(string='Fostered',
                              compute='on_change_with_fostered',
                              store=True)
    weaning_event = fields.One2many(
        comodel_name='farm.weaning.event_female_cycle',
        inverse_name='cycle', column1='event', readonly=True)
    weared = fields.Integer(string='Weared', compute='get_weaned')
    removed = fields.Integer(
        string='Removed Quantity',
        help='Number of removed animals from Produced Group. Diference '
        'between born live and weaned, computing Fostered diference.',
        compute='get_removed')
    days_between_farrowing_weaning = fields.Integer(
        string='Lactating Days',
        help='Number of days between Farrowing and Weaning.',
        compute='get_lactating_days')

    @api.one
    def update_state(self, validated_event):
        '''
        Sorted rules:
        - A cycle will be considered 'unmated'
          if weaning_event_id != False and weaning_event.state == 'validated'
          or if abort_event != False has abort_event.state == 'validated'
          or has not any validated event in insemination_event_ids.
        - A female will be considered 'lactating'
          if farrowing_event_id!=False and farrowing_event.state=='validated'
        - A female will be considered 'pregnant' if there are more than one
          diagnosis in 'validated' state and the last one has a positive result
        - A female will be considered 'mated' if there are any items in
          insemination_event_ids with 'validated' state.
        '''
        def check_event(event_to_check):
            return(type(event_to_check) == type(validated_event) and
                   event_to_check == validated_event or
                   event_to_check.state == 'validated')

        state = 'unmated'
        if (self.abort_event and check_event(self.abort_event) or
                self.weaning_event and check_event(self.weaning_event.event)):
            state = 'unmated'
        elif self.farrowing_event and check_event(self.farrowing_event.event):
            if self.farrowing_event.event.live > 0:
                state = 'lactating'
            else:
                state = 'unmated'
        elif self.pregnant:
            state = 'pregnat'
        else:
            for insemination_event in self.insemination_events:
                if check_event(insemination_event):
                    state = 'mated'
                    break
        self.state = state
        self.animal.update_state()
        self.state = state

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(FemaleCycle, self).create(vals)
        femaleCycle_obj = self.env['farm.animal.female_cycle']
        cycles = femaleCycle_obj.search([
            ('animal.id', '=', res.animal.id), ])
        secuence = 1
        for cycle in cycles:
            if len(cycle.farrowing_event) != 0:
                secuence += 1
        res.sequence = secuence
        return res

    @api.one
    def get_days_between_weaning_and_insemination(self):
        if not self.insemination_events:
            return False
        previous_cycles = self.search([
            ('animal', '=', self.animal.id),
            ('sequence', '<=', self.sequence),
            ('id', '!=', self.id)
            ],
            order='sequence, ordination_date DESC', limit=1)
        if len(previous_cycles) < 1 or (
                not previous_cycles[0].weaning_event and
                not previous_cycles[0].abort_event):
            self.days_between_wearing_and_insemination = 0
        else:
            previous_date = (
                datetime.strptime(
                    previous_cycles[0].weaning_event.event.timestamp, DFORMAT)
                if previous_cycles[0].weaning_event
                else datetime.strptime(
                    previous_cycles[0].abort_event.timestamp, DFORMAT))
            insemination_date = \
                datetime.strptime(
                    self.insemination_events[0].timestamp, DFORMAT)
            self.days_between_wearing_and_insemination = \
                (insemination_date - previous_date).days

    @api.one
    def get_live(self):
        if self.farrowing_event:
            self.live = self.farrowing_event[-1].cycle.live
        else:
            self.live = False

    @api.one
    def get_dead(self):
        if self.farrowing_event:
            self.live = self.farrowing_event[-1].cycle.dead
        else:
            self.live = False

    @api.one
    def on_change_with_fostered(self):
        self.fostered = sum(e.quantity for e in self.foster_events)

    @api.one
    def get_weaned(self):
        self.weared = self.weaning_event and \
            self.weaning_event.event.quantity or 0

    @api.one
    def get_removed(self):
        self.removed = self.live + self.fostered - self.weared

    @api.one
    def get_lactating_days(self):
        if not self.farrowing_event or not self.weaning_event:
            return None
        w_e = datetime.strptime(
            self.weaning_event[-1].event.timestamp, DFORMAT)
        f_e = datetime.strptime(
            self.farrowing_event[-1].event.timestamp, DFORMAT)
        self.days_between_farrowing_weaning = (w_e-f_e).days

    @api.one
    @api.onchange('abort_event', 'diagnosis_events', 'farrowing_event')
    def on_change_whith_pregnant(self):
        if self.abort_event:
            self.pregnant = False
        elif not self.diagnosis_events:
            self.pregnant = False
        elif self.farrowing_event:
            self.pregnant = False
        else:
            self.pregnant = \
                self.diagnosis_events[-1].result == 'positive'

    @api.one
    @api.onchange('pregnant')
    def on_change_pregnant(self):
        if self.pregnant:
            self.state = 'pregnat'

    def get_last_produced_group(self):
        farrowingEvent_obj = self.env['farm.farrowing.event']
        last_farrowing_events = farrowingEvent_obj.search([
            ('animal', '=', self),
            ('state', '=', 'validated'),
            ('produced_group', '!=', None),
            ],
            order='timestamp DESC', limit=1)
        if last_farrowing_events:
            return last_farrowing_events[0].produced_group.id
        return None
