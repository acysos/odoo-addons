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

from openerp import models, fields, api

TYPES = [('unlimited', 'unlimited'),
         ('flat', 'Flat'),
         ('shop', 'Shop'),
         ('premise', 'Premise'),
         ('chalet', 'Chalet'),
         ('house', 'House'),
         ('office', 'Office'),
         ('premise-office', 'Premise-Office'),
         ('industrial_unit', 'Industrial Unit'),
         ('hotel_industry', 'Hotel Industry'),
         ('parking', 'Parking'),
         ('box_room', 'Box room'),
         ('land', 'Land')]

OWNER_TYPE = [('none', 'None'),
              ('public', 'Public'),
              ('private', 'Private')]


class real_estate_zone(models.Model):
    _name = 'real.estate.zone'
    name = fields.Char('Zone', required=True, translate=True)
    city_id = fields.Many2one(
        'res.better.zip', 'Location', required=False,
        help='Usa el nombre o el C.P para buscar la localización')
    _order = "name"


class real_estate_situation(models.Model):
    _name = 'real.estate.situation'
    name = fields.Char('Situation', required=True, translate=True)
    _order = "name"


class real_estate_heating(models.Model):
    _name = 'real.estate.heating'
    name = fields.Char('Heating', required=True, translate=True)
    _order = "name"


class real_estate_hotwater(models.Model):
    _name = 'real.estate.hotwater'
    name = fields.Char('Hot Water', required=True, translate=True)
    _order = "name"


class real_estate_land_type(models.Model):
    _name = 'real.estate.land.type'
    name = fields.Char('Land Type', required=True, translate=True)
    _order = "name"


class real_estate_land_state(models.Model):
    _name = 'real.estate.land.state'
    name = fields.Char('Land State', required=True, translate=True)
    _order = "name"


class real_estate_class(models.Model):
    _name = 'real.estate.class'
    name = fields.Char('Class', required=True, translate=True)
    _order = "name"


class real_estate_investiment(models.Model):
    _name = 'real.estate.investiment'
    name = fields.Char('Investiment', required=True, translate=True)
    _order = "name"


class real_estate_status(models.Model):
    _name = 'real.estate.status'
    name = fields.Char('Status', required=True, translate=True)
    _order = "name"


class real_estate_subtype(models.Model):
    _name = 'real.estate.subtype'
    name = fields.Char('Subtype', required=True, translate=True)
    type = fields.Selection(TYPES, string='Top Type')
    _order = "name"


class real_estate_top_subdivision(models.Model):
    _name = 'real.estate.top.subsivision'
    _description = 'Top subdivision that can be rented individually'

    name = fields.Char('Name', default='/', required=False,
                       readonly=False, translate=True)
    m2 = fields.Integer('M2')
    top_id = fields.Many2one(comodel_name='real.estate.top', string='Top',
                             ondelete='cascade')


class real_estate_rental_type(models.Model):
    _name = 'real.estate.rental.type'
    name = fields.Char('Rental Type', required=True, translate=True)
    _order = "name"


class real_estate_ac(models.Model):
    _name = 'real.estate.ac'
    name = fields.Char('Air Conditioning', required=True, translate=True)
    _order = "name"


class real_estate_noise_level(models.Model):
    _name = 'real.estate.noise.level'
    name = fields.Char('Noise Level', required=True, translate=True)
    _order = "name"


class real_estate_access(models.Model):
    _name = 'real.estate.access'
    name = fields.Char('Access', required=True, translate=True)
    _order = "name"


class real_estate_floot_type(models.Model):
    _name = 'real.estate.floor.type'
    name = fields.Char('Floor Type', required=True, translate=True)
    _order = "name"


class RealEstateWindow(models.Model):
    _name = 'real.estate.window'
    name = fields.Char('Windows', required=True, translate=True)
    _order = "name"


class RealEstateWindowGlass(models.Model):
    _name = 'real.estate.windowglass'
    name = fields.Char('Window Glass', required=True, translate=True)
    _order = "name"


class RealEstateSunny(models.Model):
    _name = 'real.estate.sunny'
    name = fields.Char('Sunny', required=True, translate=True)
    _order = "name"


class RealEstateView(models.Model):
    _name = 'real.estate.view'
    name = fields.Char('View', required=True, translate=True)
    _order = "name"


class RealEstateFurniture(models.Model):
    _name = 'real.estate.furniture'
    name = fields.Char('Furniture', required=True, translate=True)
    _order = "name"


class RealEstateSewerage(models.Model):
    _name = 'real.estate.sewerage'
    name = fields.Char('Sewerage', required=True, translate=True)
    _order = "name"


class RealEstateAwning(models.Model):
    _name = 'real.estate.awning'
    name = fields.Char('Awning', required=True, translate=True)
    _order = "name"


class real_estate_top(models.Model):
    _name = 'real.estate.top'

    @api.depends('flat_usage_m2', 'ground_m2', 'office_m2', 'chalet_usage_m2',
                 'land_m2')
    def _m2_get(self):
        for top in self:
            if top.type in ['flat']:
                top.m2 = top.flat_usage_m2
            elif top.type in ['shop', 'industrial_unit', 'hotel_industry',
                              'premise']:
                top.m2 = top.ground_m2
            elif top.type in ['office', 'premise-office']:
                top.m2 = top.office_m2
            elif top.type in ['chalet', 'house']:
                top.m2 = top.chalet_usage_m2
            elif top.type in ['land']:
                top.m2 = top.land_m2
            else:
                top.m2 = 0

    @api.multi
    def _cons_m2_get(self):
        for top in self:
            if top.type in ['flat']:
                top.cons_m2 = top.flat_cons_m2
            elif top.type in ['shop', 'industrial_unit', 'hotel_industry',
                              'premise']:
                top.cons_m2 = top.ground_cons_m2
            elif top.type in ['office', 'premise-office']:
                top.cons_m2 = top.office_cons_m2
            elif top.type in ['chalet', 'house']:
                top.cons_m2 = top.chalet_cons_m2
            elif top.type in ['land']:
                top.cons_m2 = top.land_cons_m2
            else:
                top.cons_m2 = 0

    OPERATIONS = [('sale', 'Sale'),
                  ('rent', 'Rent'),
                  ('sale_rent', 'Sale & Rent'),
                  ('rent_sale_option', 'Rent with sale option'),
                  ('new_development', 'New development'),
                  ('transfer', 'Transfer'),
                  ('valuation', 'Valuation')]

    RENTAL_TYPE = [('both', 'Both'),
                   ('holiday', 'Holiday/Short Term'),
                   ('long', 'Long Term')]

    INCLUDED = [('included', 'Included'),
                ('included_up_to', 'Included up to'),
                ('not_included', 'Not Included')]

    ENERGY_EFFICIENCY = [('in_process', 'In process'),
                         ('exempt', 'Exempt'),
                         ('yes', 'Yes'),
                         ('a', 'A'),
                         ('b', 'B'),
                         ('c', 'C'),
                         ('d', 'D'),
                         ('e', 'E'),
                         ('f', 'F'),
                         ('g', 'G')]

    ORIENTATION = [('all', 'All'),
                   ('north', 'North'),
                   ('northeast', 'Northeast'),
                   ('east', 'East'),
                   ('southeast', 'South-Easth'),
                   ('south', 'South'),
                   ('southwest', 'South West'),
                   ('west', 'West'),
                   ('northwest', 'Northwest'),
                   ('north-south', 'North-South'),
                   ('east-west', 'East-West')]

    FURNISHED = [('yes', 'Yes'),
                 ('half', 'Half'),
                 ('no', 'No')]

    create_date = fields.Datetime('Create Date', readonly=True)
    write_date = fields.Datetime('Last Write Date', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson')
    name = fields.Char('Reference', readonly=True)
    address = fields.Char('Address', required=True)
    situation = fields.Many2one(
        comodel_name='real.estate.situation', string='Situation')
    stair = fields.Char('Stair')
    number = fields.Char('Number')
    floor = fields.Char('Floor')
    type = fields.Selection(TYPES, 'Type', default='unlimited', required=True)
    zone = fields.Many2one('real.estate.zone', 'Zone', required=True)
    city_id = fields.Many2one(
        'res.better.zip', 'Location', required=False,
        help='Usa el nombre o el C.P para buscar la localización')
    partner_id = fields.Many2one(
        'res.partner', 'Owner',
        domain=[('real_estate_type', '=', 'owner')])
    operation = fields.Selection(OPERATIONS, 'Operation', default='sale',
                                 required=True)
    rental_type = fields.Selection(RENTAL_TYPE, string='Rental Type')
    date = fields.Date('Date', required=True)
    updated_date = fields.Date('Updated Date')
    number_keys = fields.Char('Number of Keys')
    exclusive = fields.Boolean('Exclusive')
    exclusive_date = fields.Date('Exclusive Date')
    agreements = fields.One2many('rental.agreement', 'top_id',
                                 'Rental Agreements')
    attachments_url = fields.Char(string='Attachments URL')
    # Common information
    sale_price = fields.Float('Sale Price')
    rent_price = fields.Float('Rent Price')
    homeowners_expenses = fields.Char('Homeowners Amount')
    homeowners_expenses_included = fields.Selection(
        selection=INCLUDED, string='Homeowners Expenses')
    deposit = fields.Char('Deposit')
    deposit_date = fields.Datetime(string='Deposit Date')
    deposit_amount = fields.Float(string='Deposit Amount')
    note = fields.Text('Notes')
    available = fields.Boolean('Available', default=lambda *a: 1)
    subtype = fields.Many2one('real.estate.subtype', 'Subtype')
    top_class = fields.Many2one(
        comodel_name='real.estate.class', string='Class')
    investiment = fields.Many2one(
        comodel_name='real.estate.investiment', string='Investiment')
    status = fields.Many2one(
        comodel_name='real.estate.status', string='Status')
    operation_state = fields.Selection([
            ('none', 'None'),
            ('pending_sold', 'Pending Sold'),
            ('pending_rented', 'Pending Rented'),
            ('sold', 'Sold'),
            ('rented', 'Rented'),
            ], 'State', select=True, readonly=False)
    energy_efficiency = fields.Selection(ENERGY_EFFICIENCY,
                                         'Energy Efficiency',
                                         default='in_process', required=False)
    energy_date = fields.Date('Date Energy Efficiency')
    energy_emission = fields.Integer('Energy Emission')
    energy_number = fields.Integer('Energy Number')
    energy_doc = fields.Binary('Energy Certificate')
    doc_filename = fields.Char("Doc Filename")
    retribution = fields.Char('Retribution')
    buyer_id = fields.Many2one('res.partner', 'Buyer',
                               domain=[('real_estate_type', '=', 'buyer')])
    m2 = fields.Float(compute='_m2_get', string='M2', store=True)
    cons_m2 = fields.Float(compute='_cons_m2_get', string='Constructed M2',
                           store=False)
    subdivision_ids = fields.One2many(
        comodel_name='real.estate.top.subsivision', inverse_name='top_id',
        string='Subdivisions', required=False)
    # Flat, Chalet, Town House information
    kitchen = fields.Integer('Kitchen')
    kitchen_description = fields.Char('Kitchen Description')
    dinningroom = fields.Integer(string='Dinning Rooms')
    dinningroom_description = fields.Char('Dinningroom Description')
    hall = fields.Integer('Hall')
    hall_description = fields.Char('Hall Description')
    rooms = fields.Integer('Rooms')
    room_description = fields.Char('Room Description')
    bathroom = fields.Integer('Bathroom')
    bath_description = fields.Char('Bathroom Description')
    toilet = fields.Integer('Toilet')
    toilet_description = fields.Char('Toilet Description')
    orientation = fields.Selection(ORIENTATION, 'Orientation')
    parking = fields.Integer('Parking')
    parking_description = fields.Char('Parking Description')
    parking_type = fields.Selection(
        selection=OWNER_TYPE, string='Parking type')
    box_room = fields.Integer('Box Room')
    box_room_description = fields.Char('Box Room Description')
    outside = fields.Boolean('Outside')
    balcony = fields.Char('Balcony')
    balcony_public = fields.Integer(string='Balcony')
    balcony_private = fields.Integer(string='Balcony')
    note_flat = fields.Text('Notes')
    attics = fields.Integer(string='Attics')
    basements = fields.Integer(string='Basements')
    cellars = fields.Integer(string='Cellars')
    conservatories = fields.Integer(string='Conservatories')
    dishwashers = fields.Integer(string='Dish Washers')
    tumbledryers = fields.Integer(string='Tumble Dryers')
    fireplaces = fields.Integer(string='Fireplaces')
    guestrooms = fields.Integer(string='Guest Rooms')
    laundryrooms = fields.Integer(string='Laundry Rooms')
    levels = fields.Integer(string='Levels')
    libraries = fields.Integer(string='Libraries')
    lofts = fields.Integer(string='Lofts')
    lounges = fields.Integer(string='Lounges')
    offices = fields.Integer(string='Offices')
    playrooms = fields.Integer(string='Play Rooms')
    pooltables = fields.Integer(string='Pool Tables')
    refrigerators = fields.Integer(string='Refrigerators')
    storagerooms = fields.Integer(string='Storage Rooms')
    stoves = fields.Integer(string='Stoves')
    studyrooms = fields.Integer(string='Study Rooms')
    phonelines = fields.Integer(string='Phone Lines')
    tvs = fields.Integer(string='TVs')
    tvflat = fields.Integer(string='TVflat')
    homecinemas = fields.Integer(string='Home Cinemas')
    cotbeds = fields.Integer(string='Cotbeds')
    playpens = fields.Integer(string='PlayPens')
    ventilators = fields.Integer(string='Ventilators')
    washingmachines = fields.Integer(string='WashingMachines')
    waterwell = fields.Integer(string='Water Well')
    croft_public = fields.Integer(string='Croft')
    croft_private = fields.Integer(string='Croft')
    garden_public = fields.Integer(string='Garden')
    garden_private = fields.Integer(string='Garden')
    gardenshed_public = fields.Integer(string='Garden shed')
    gardenshed_private = fields.Integer(string='Garden shed')
    terraces_public = fields.Integer(string='Terraces')
    terraces_private = fields.Integer(string='Terraces')
    roof_terraces_public = fields.Integer(string='Roof Terraces')
    roof_terraces_private = fields.Integer(string='Roof Terraces')
    parkingspot_public = fields.Integer(string='Parking spot public')
    parkingspot_private = fields.Integer(string='Parking spot private')
    spa_public = fields.Integer(string='SPA')
    spa_private = fields.Integer(string='SPA')
    gym = fields.Integer(string='Gym')
    gym_type = fields.Selection(
        selection=OWNER_TYPE, string='Gym type')
    barbacue = fields.Integer(string='Barbacue')
    workshop = fields.Integer(string='Workshop')
    managed = fields.Boolean(string='Managed')
    home_air_conditioning = fields.Many2one(
        comodel_name='real.estate.ac', string='Air Conditioning')
    noise_level = fields.Many2one(
        comodel_name='real.estate.noise.level', string='Noise level')
    access = fields.Many2one(
        comodel_name='real.estate.access', string='Access')
    floor_type = fields.Many2one(
        comodel_name='real.estate.floor.type', string='Floor Type')
    window = fields.Many2one(
        comodel_name='real.estate.window', string='Windows')
    window_glass = fields.Many2one(
        comodel_name='real.estate.windowglass', string='Window Glass')
    sunny = fields.Many2one(
        comodel_name='real.estate.sunny', string='Light level')
    view = fields.Many2one(
        comodel_name='real.estate.view', string='Views')
    furniture = fields.Many2one(
        comodel_name='real.estate.furniture', string='Furniture')
    sewerage = fields.Many2one(
        comodel_name='real.estate.sewerage', string='Sewerage')
    awning = fields.Many2one(
        comodel_name='real.estate.awning', string='Awning')
    alarm = fields.Boolean(string='Alarm')
    appfloor = fields.Boolean(string='AppFloor')
    auto_watering = fields.Boolean(string='Auto Watering')
    broadband = fields.Boolean(string='Broadband')
    cable = fields.Boolean(string='Cable')
    driveway = fields.Boolean(string='Driveway')
    electricity = fields.Boolean(string='Electricity')
    elevated = fields.Boolean(string='Elevated')
    elevator = fields.Boolean(string='Elevator')
    gas = fields.Boolean(string='Gas')
    heated_floors = fields.Boolean(string='Heated Floors')
    hiking = fields.Boolean(string='Hiking')
    satellite = fields.Boolean(string='Satellite')
    security_doors = fields.Boolean(string='Security Doors')
    breeze_through = fields.Boolean(string='Breeze Through')
    safe = fields.Boolean(string='Safe')
    solar_heater = fields.Boolean(string='Solar Heater')
    solar_panels = fields.Boolean(string='Solar Panels')
    sound_proof = fields.Boolean(string='Sound Proof')
    tv = fields.Boolean(string='TV')
    water = fields.Boolean(string='Water')
    water_drill = fields.Boolean(string='Water Drill')
    wind_mill = fields.Boolean(string='Wind Mill')
    window_screens = fields.Boolean(string='Window Screens')
    window_shutters = fields.Boolean(string='Window Shutters')
    resale = fields.Boolean(string='Resale')
    special_site_acces = fields.Boolean(string='Site Access')
    special_bathrooms = fields.Boolean(string='Bathroom')
    special_entrance = fields.Boolean(string='Entrance')
    special_kitchen = fields.Boolean(string='Kitchen')
    special_elderly = fields.Boolean(string='Elderly')
    insulation_under = fields.Boolean(string='Insulation Under')
    insulation_over = fields.Boolean(string='Insulation Over')
    cycling = fields.Boolean(string='Cycling')
    electricity_generator = fields.Boolean(string='Eletricity Generator')
    pet_friendly_prop = fields.Boolean(string='Pet Friendly Prop')
    pet_friendly_loc = fields.Boolean(string='Pet Friendly Loc')
    cookware = fields.Boolean(string='Cookware')
    kettles = fields.Boolean(string='Kettles')
    ironing_boards = fields.Boolean(string='Ironing Board')
    toasters = fields.Boolean(string='Toasters')
    linen = fields.Boolean(string='Linen')
    hairdryers = fields.Boolean(string='Hairdryers')
    blankets = fields.Boolean(string='Blankets')
    towels = fields.Boolean(string='Towels')
    microwaves = fields.Boolean(string='Microwaves')
    irons = fields.Boolean(string='Irons')
    coffee_makers = fields.Boolean(string='Coffee Makers')
    dvd = fields.Boolean(string='DVD')
    hifi = fields.Boolean(string='HiFi')
    tennis_court_public = fields.Boolean(string='Tennis Court Public')
    tennis_court_private = fields.Boolean(string='Tennis Court Private')
    play_area_public = fields.Boolean(string='Play Area Public')
    play_area_private = fields.Boolean(string='Play Area Private')
    sleeps = fields.Boolean(string='Sleeps')
    dinnerware = fields.Boolean(string='Dinnerware')
    construction_year = fields.Integer(string="Construction year")
    # Rent Flat, Chalet or Town house
    bedrooms = fields.Integer('Bedrooms')
    built_in_closet = fields.Integer('Built-in Closet')
    furnished = fields.Selection(FURNISHED, 'Furnished')
    furnished_description = fields.Char('Furnished Description')
    # Suppliers
    administrator = fields.Char('Administrator')
    administrator_phone = fields.Char('Telephone')
    email = fields.Char('E-Mail')
    website = fields.Char('Website',
                          help="Website of Administrator")
    light_ref = fields.Char('Light Reference')
    light_fee_included = fields.Selection(
        selection=INCLUDED, string="Light Fee")
    light_fee = fields.Float(string='Light Fee Amount')
    gas_ref = fields.Char('Gas Reference')
    gas_fee_included = fields.Selection(selection=INCLUDED, string="Gas Fee")
    gas_fee = fields.Float(string='Gas Fee Amount')
    water_ref = fields.Char('Water Reference')
    water_fee_included = fields.Selection(
        selection=INCLUDED, string="Water Fee")
    water_fee = fields.Float(string='Water Fee Amount')
    # Only Flat.
    flat_usage_m2 = fields.Float('Usage M2')
    flat_cons_m2 = fields.Float('Constructed M2')
    elevator = fields.Boolean('Elevator')
    flat_heating = fields.Many2one('real.estate.heating', 'Heating')
    flat_hotwater = fields.Many2one('real.estate.hotwater', 'Hot Water')
    students = fields.Boolean('Estudiantes')
    # Only Chalet, Town House
    chalet_usage_m2 = fields.Float('Usage M2')
    chalet_cons_m2 = fields.Float('Constructed M2')
    plot_m2 = fields.Float('Plot M2')
    chalet_basement = fields.Float('Basement')
    chalet_ground = fields.Float('Ground')
    first_floor = fields.Float('First Floor')
    second_floor = fields.Float('Second Floor')
    garden_m2 = fields.Float('Garden M2')
    swimming_pool = fields.Boolean('Swimming Pool')
    swimming_pool_sea_public = fields.Integer(string='Sea')
    swimming_pool_sea_private = fields.Integer(string='Sea')
    swimming_pool_indoor_public = fields.Integer(string='Indoor')
    swimming_pool_indoor_private = fields.Integer(string='Indoor')
    swimming_pool_outdoor_public = fields.Integer(string='Outdoor')
    swimming_pool_outdoor_private = fields.Integer(string='Outdoor')
    swimming_pool_heated_public = fields.Integer(string='Heated')
    swimming_pool_heated_private = fields.Integer(string='Heated')
    swimming_pool_kids_public = fields.Integer(string='Kids')
    swimming_pool_kids_private = fields.Integer(string='Kids')
    floor_number = fields.Integer('Floor Number')
    chalet_heating = fields.Many2one('real.estate.heating', 'Heating')
    chalet_hotwater = fields.Many2one('real.estate.hotwater', 'Hot Water')
    # Industrial Unit information
    ground_m2 = fields.Float('Ground M2')
    ground_cons_m2 = fields.Float('Constructed M2')
    mezzanine_m2 = fields.Float('Mezzanine M2')
    basement_m2 = fields.Float('Basement M2')
    open_field_m2 = fields.Float('Open Field M2')
    height = fields.Float('Height')
    electricity = fields.Boolean('Eletricity')
    triphase = fields.Boolean('Triphase')
    locker_room = fields.Integer('Locker Room')
    offices = fields.Integer('Offices')
    fire_fighting = fields.Char('Fire-Fighting')
    gantry_crane = fields.Char('Gantry Crane')
    shop_window = fields.Char('Shop Window')
    industrial_toilet = fields.Integer('Toilet')
    industrial_prepared = fields.Boolean('Prepared')
#   Office information
    office_m2 = fields.Float('Office M2')
    office_cons_m2 = fields.Float('Constructed Office M2')
    office_electricity = fields.Boolean('Eletricity')
    office_toilets = fields.Char('Toilets')
    office_toilet_description = fields.Char('Toilet Description')
    office_outside = fields.Boolean('Outside')
    office_elevator = fields.Boolean('Elevator')
    office_heating = fields.Many2one('real.estate.heating', 'Heating')
    office_air_conditioning = fields.Many2one(
        comodel_name='real.estate.ac', string='Air Conditioning')
    structural_barriers = fields.Boolean('Structural Barriers')
    office_parking = fields.Char('Parking')
    office_boxroom = fields.Char('Box Room')
#   Shop and Premise Information
    shop_electricity = fields.Boolean('Eletricity')
    shop_toilet = fields.Integer('Toilet')
    shop_facade = fields.Char('Facade')
    shop_heating = fields.Many2one('real.estate.heating', 'Heating')
    shop_air_conditioning = fields.Many2one(
        comodel_name='real.estate.ac', string='Air Conditioning')
    shop_prepared = fields.Boolean('Prepared')
#   Hotel industry
    fumes_vent = fields.Boolean('Fumes Vent')
#   Land
    land_m2 = fields.Float('Land M2')
    land_cons_m2 = fields.Float('Usage Land M2')
    land_type = fields.Many2one('real.estate.land.type', 'Land Type')
    land_state = fields.Many2one('real.estate.land.state', 'Land state')
#   meetings
    top_meetings = fields.Integer(compute='tops_meetings_count',
                                  string='Top Meetings', store=False)


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('real.estate.top')
        res = super(real_estate_top, self).create(vals)
        return res

    @api.multi
    def tops_meetings_count(self):
        for top in self:
            num_meetings = len(self.env['calendar.event'].search(
                [('top_id', '=', top.id)]))
            top.top_meetings = num_meetings
