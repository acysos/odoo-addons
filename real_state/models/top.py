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

from openerp import models, fields, api, _


class real_state_zone(models.Model):
   _name = 'real.state.zone'
   name = fields.Char('Zone', required=True, size=64)
   _order = "name"
   
class real_state_heating(models.Model):
    _name = 'real.state.heating'
    name = fields.Char('Heating', required=True, size=64)
    _order = "name"


class real_state_hotwater(models.Model):
    _name = 'real.state.hotwater'
    name = fields.Char('Hot Water', required=True, size=64)
    _order = "name"

class real_state_land_type(models.Model):
    _name = 'real.state.land.type'
    name = fields.Char('Land Type', required=True, size=64)
    _order = "name"

class real_state_land_state(models.Model):
    _name = 'real.state.land.state'
    name = fields.Char('Land State', required=True, size=64)
    _order = "name"

class real_state_subtype(models.Model):
    _name = 'real.state.subtype'
    name = fields.Char('Subtype', required=True, size=64)
    type = fields.Selection([('unlimited','unlimited'),
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
                        ('land','Land')], 'Top Type', required=True, select=True)
    _order = "name"


class real_state_top_subdivision(models.Model):
    _name = 'real.state.top.subsivision'
    _description= 'Top subdivision that can be rented individually'
    
    name = fields.Char('Name', default='/', size=64, required=False, 
                       readonly=False)
    m2 = fields.Integer('M2')
    top_id = fields.Many2one(comodel_name='real.state.top', string='Top', 
                             ondelete='cascade')


class real_state_top(models.Model):
    _name = 'real.state.top'
    
    
    @api.multi
    def _get_mount_point(self):
        user = self.env.user
        print user
        company = user.company_id
        print company
        for top in self:
            if user.document_mount:
                mount = user.default_mount_agreement
                print mount
            else:
                mount = company.default_mount_agreement
                print mount
            if user.document_client:
                client = user.document_client
                print client
            else:
                client = company.default_document_client
                print client
            model_id = self.env['ir.model'].search([('model','=',
                                                     'real.state.top')])
            print model_id
            dir_obj = self.env['document.directory']
            dir_id = dir_obj.search([('ressource_type_id','=',model_id.id),
                                     ('domain','=','[]')])
            print dir_id.name
            print top.name
            path = ''
            if client == 'unix':
                path = mount + 'Real_State' + '/' + top.name + '/'
            elif client == 'win':
                path = mount + 'Real_State' + '\\' + top.name + '\\'
            top.attachments_url = path
    
        
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
            elif top.type in ['chalet','house']:
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
            elif top.type in ['office','premise-office']:
                top.cons_m2 = top.office_cons_m2
            elif top.type in ['chalet','house']:
                top.cons_m2 = top.chalet_cons_m2
            elif top.type in ['land']:
                top.cons_m2 = top.land_cons_m2
            else:
                top.cons_m2 = 0
    
    
    
    TYPES = [('unlimited','unlimited'),
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
    
    OPERATIONS = [('sale','Sale'),
                  ('rent','Rent'),
                  ('sale_rent','Sale & Rent'),
                  ('rent_sale_option','Rent with sale option'),
                  ('transfer','Transfer'),
                  ('valuation','Valuation')]
    
    ENERGY_EFFICIENCY = [('in_process','In process'),
                          ('exempt','Exempt'),
                          ('yes','Yes'),
                          ('a','A'),
                          ('b','B'),
                          ('c','C'),
                          ('d','D'),
                          ('e','E'),
                          ('f','F'),
                          ('g','G')]
    
    ORIENTATION = [('all','All'),
                   ('north','North'),
                   ('northeast','Northeast'),
                   ('east','East'),
                   ('southeast','South-Easth'),
                   ('south','South'),
                   ('southwest','South West'),
                   ('west','West'),
                   ('northwest','Northwest'),
                   ('north-south','North-South'),
                   ('east-west','East-West')]
    
    FURNISHED = [('yes','Yes'),
                 ('half','Half'),
                 ('no','No')]
 
    create_date = fields.Datetime('Create Date', readonly=True)
    write_date = fields.Datetime('Last Write Date', readonly=True)
    name = fields.Char('Reference', size=64, select=True, readonly=True)
    address = fields.Char('Address', size=256, required=True)
    stair = fields.Char('Stair', size=256)
    number = fields.Char('Number', size=64, select=True)
    floor = fields.Char('Floor', size=64, select=True)
    type = fields.Selection(TYPES, 'Type', default='unlimited', required=True, 
                            select=True)
    zone = fields.Many2one('real.state.zone','Zone', required=True, select=True)
    city_id = fields.Many2one('res.better.zip', 'Location', required=False, 
                    help='Usa el nombre o el C.P para buscar la localización')
    partner_id = fields.Many2one('res.partner','Owner', select=True, 
                                 domain= [('real_state_type','=','owner')])
    operation = fields.Selection(OPERATIONS, 'Operation', default='sale', 
                                 required=True, select=True)
    date = fields.Date('Date', required=True)
    updated_date = fields.Date('Updated Date')
    number_keys = fields.Char('Number of Keys', size=256)
    exclusive = fields.Boolean('Exclusive')
    exclusive_date = fields.Date('Exclusive Date')
    agreements = fields.One2many('rental.agreement', 'top_id', 
                                 'Rental Agreements')
    attachments_url = fields.Char(compute='_get_mount_point', store=False, 
                                  size=1024, string='Attachments URL')
    # Common information
    sale_price = fields.Float('Sale Price')
    rent_price = fields.Float('Rent Price')
    homeowners_expenses = fields.Char('Homeowners Expenses',size=256)
    homeowners_expenses_included = fields.Boolean('Included')
    deposit = fields.Char('Deposit', size=256)
    note = fields.Text('Notes')
    available = fields.Boolean('Available', default=lambda *a: 1)
    subtype = fields.Many2one('real.state.subtype','Subtype', select=True)
    energy_efficiency = fields.Selection(ENERGY_EFFICIENCY, 
                                         'Energy Efficiency', 
                                         default='in_process', required=False)
    energy_date = fields.Date('Date Energy Efficiency')
    energy_emission = fields.Integer('Energy Emission')
    energy_number = fields.Integer('Energy Number')
    energy_doc = fields.Binary('Energy Certificate')
    retribution = fields.Char('Retribution', size=256)
    buyer_id = fields.Many2one('res.partner','Buyer', 
                               domain= [('real_state_type','=','buyer')])
    m2 = fields.Float(compute='_m2_get', string='M2', store=True)
    cons_m2 = fields.Float(compute='_cons_m2_get', string='Constructed M2', 
                           store=False)
    subdivision_ids = fields.One2many(
        comodel_name='real.state.top.subsivision', inverse_name='top_id', 
        string='Subdivisions', required=False)
    # Flat, Chalet, Town House information
    kitchen = fields.Integer('Kitchen')
    kitchen_description = fields.Char('Kitchen Description', size=256)
    hall = fields.Integer('Hall')
    hall_description = fields.Char('Hall Description', size=256)
    rooms = fields.Integer('Rooms')
    room_description = fields.Char('Room Description', size=256)
    bathroom = fields.Integer('Bathroom')
    bath_description = fields.Char('Bathroom Description', size=256)
    toilet = fields.Integer('Toilet')
    toilet_description = fields.Char('Toilet Description', size=256)
    orientation = fields.Selection(ORIENTATION, 'Orientation')
    parking = fields.Integer('Parking')
    parking_description = fields.Char('Parking Description', size=256)
    box_room = fields.Integer('Box Room')
    box_room_description = fields.Char('Box Room Description', size=256)
    outside = fields.Boolean('Outside')
    balcony = fields.Char('Balcony', size=256)
    note_flat = fields.Text('Notes')
    # Rent Flat, Chalet or Town house
    bedrooms = fields.Integer('Bedrooms')
    built_in_closet = fields.Integer('Built-in Closet')
    furnished = fields.Selection(FURNISHED, 'Furnished')
    furnished_description = fields.Char('Furnished Description', size=256)
    # Suppliers
    administrator = fields.Char('Administrator',size=256)
    administrator_phone = fields.Char('Telephone',size=256)
    email = fields.Char('E-Mail', size=256)
    website = fields.Char('Website',size=256, 
                          help="Website of Administrator")
    light_ref = fields.Char('Light Reference',size=256)
    gas_ref = fields.Char('Gas Reference',size=256)
    aqua_ref = fields.Char('Aqua Reference',size=256)
    # Only Flat.
    flat_usage_m2 = fields.Float('Usage M2')
    flat_cons_m2 = fields.Float('Constructed M2')
    elevator = fields.Boolean('Elevator')
    flat_heating = fields.Many2one('real.state.heating','Heating')
    flat_hotwater = fields.Many2one('real.state.hotwater','Hot Water')
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
    floor_number = fields.Integer('Floor Number')
    chalet_heating = fields.Many2one('real.state.heating','Heating')
    chalet_hotwater = fields.Many2one('real.state.hotwater','Hot Water')
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
    fire_fighting = fields.Char('Fire-Fighting',size=256)
    gantry_crane = fields.Char('Gantry Crane',size=256)
    shop_window = fields.Char('Shop Window',size=256)
    industrial_toilet = fields.Integer('Toilet')
    industrial_prepared = fields.Boolean('Prepared')
    #Office information
    office_m2 = fields.Float('Office M2')
    office_cons_m2 = fields.Float('Constructed Office M2')
    office_electricity = fields.Boolean('Eletricity')
    office_toilets = fields.Char('Toilets',size=256)
    office_outside = fields.Boolean('Outside')
    office_elevator = fields.Boolean('Elevator')
    office_heating = fields.Many2one('real.state.heating','Heating')
    office_air_conditioning = fields.Char('Air Conditioning',size=256)
    structural_barriers = fields.Boolean('Structural Barriers')
    office_parking = fields.Char('Parking',size=256)
    office_boxroom = fields.Char('Box Room',size=256)
    #Shop and Premise Information
    shop_electricity = fields.Boolean('Eletricity')
    shop_toilet = fields.Integer('Toilet')
    shop_facade = fields.Char('Facade',size=256)
    shop_heating = fields.Many2one('real.state.heating','Heating')
    shop_air_conditioning = fields.Boolean('Air Conditioning')
    shop_prepared = fields.Boolean('Prepared')
    #Hotel industry
    fumes_vent = fields.Boolean('Fumes Vent')
    #Land
    land_m2 = fields.Float('Land M2')
    land_cons_m2 = fields.Float('Usage Land M2')
    land_type = fields.Many2one('real.state.land.type','Land Type')
    land_state = fields.Many2one('real.state.land.state','Land State')
    #meetings
    top_meetings = fields.Integer(compute='tops_meetings_count',
                                  string='Top Meetings', store=False)
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('real.state.top')
        res = super(real_state_top, self).create(vals)
        return res
    
    @api.multi
    def tops_meetings_count(self):
        for top in self:
            num_meetings = len(self.env['calendar.event'].search(
                [('top_id', '=', top.id)]))
            print num_meetings
            top.top_meetings = num_meetings


    
