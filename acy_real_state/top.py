# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
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

from osv import fields,osv
from tools.translate import _

class real_state_zone(osv.osv):
    _name = 'real.state.zone'
    _columns = {
        'name': fields.char('Zone', required=True, size=64),
    }
    _order = 'name'
real_state_zone()

class real_state_heating(osv.osv):
    _name = 'real.state.heating'
    _columns = {
        'name': fields.char('Heating', required=True, size=64),
    }
    _order = 'name'
real_state_heating()

class real_state_hotwater(osv.osv):
    _name = 'real.state.hotwater'
    _columns = {
        'name': fields.char('Hot Water', required=True, size=64),
    }
    _order = 'name'
real_state_hotwater()

class real_state_land_type(osv.osv):
    _name = 'real.state.land.type'
    _columns = {
        'name': fields.char('Land Type', required=True, size=64),
    }
    _order = 'name'
real_state_land_type()

class real_state_land_state(osv.osv):
    _name = 'real.state.land.state'
    _columns = {
        'name': fields.char('Land State', required=True, size=64),
    }
    _order = 'name'
real_state_land_state()

class real_state_subtype(osv.osv):
    _name = 'real.state.subtype'
    _columns = {
        'name': fields.char('SubType', required=True, size=64),
        'type': fields.selection([('unlimited','unlimited'),
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
                        ('land','Land')], 'Top Type', required=True, select=True),
    }
    _order = 'name'
real_state_subtype()

class real_state_top_subdivision(osv.osv):
    _name = 'real.state.top.subsivision'
    _description= 'Top subdivision that can be rented individually'
    
    _columns = {
        'name':fields.char('Name', size=64, required=False, readonly=False), 
        'm2': fields.integer('M2'),
        'top_id': fields.many2one('real.state.top', 'Top', ondelete='cascade'),
    }
    
    _defaults = {  
        'name': '/',  
        }
    
real_state_top_subdivision()

class real_state_top(osv.osv):
    _name = 'real.state.top'
    
    def _get_mount_point(self,cr,uid,ids,name,arg,context={}):
        res = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        for top in self.browse(cr,uid,ids,context):
            if user.document_mount:
                mount = user.document_mount
            else:
                mount = company.default_document_mount
            if user.document_client:
                client = user.document_client
            else:
                client = company.default_document_client
            model_obj = self.pool.get('ir.model')
            model_id = model_obj.search(cr,uid,[('model','=','real.state.top')])[0]
            dir_obj = self.pool.get('document.directory')
            dir_id = dir_obj.search(cr,uid,[('ressource_type_id','=',model_id),('domain','=','[]')])[0]
            diry = dir_obj.browse(cr,uid,dir_id,context)
            path = ''
            if client == 'unix':
                path = mount + diry.name + '/' + top.name + '/'
            elif client == 'win':
                path = mount + diry.name + '\\' + top.name + '\\'
            elif client == 'web':
                data_pool = self.pool.get('ir.model.data')
                aid = data_pool._get_id(cr, uid, 'document_ftp', 'action_document_browse')
                aid = data_pool.browse(cr, uid, aid, context=context).res_id
                ftp_url = self.pool.get('ir.actions.url').browse(cr, uid, aid, context=context)
                url = ftp_url.url and ftp_url.url.split('ftp://') or []
                if url:
                    url = url[1]
                    if url[-1] == '/':
                        url = url[:-1]
                else:
                    url = '%s:%s' %(ftpserver.HOST, ftpserver.PORT)
                path = 'ftp://%s@%s'%(user.login, url) + '/' + diry.name + '/' + top.name + '/'
            res[top.id] = path
        return res

    def _m2_get(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for top in self.browse(cr, uid, ids, context):
            if top.type in ['flat']:
                res[top.id] = top.flat_usage_m2
            elif top.type in ['shop', 'industrial_unit', 'hotel_industry', 'premise']:
                res[top.id] = top.ground_m2
            elif top.type in ['office', 'premise-office']:
                res[top.id] = top.office_m2
            elif top.type in ['chalet','house']:
                res[top.id] = top.chalet_usage_m2
            elif top.type in ['land']:
                res[top.id] = top.land_m2
            else:
                res[top.id] = 0
        return res
    
    def _cons_m2_get(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for top in self.browse(cr, uid, ids, context):
            if top.type in ['flat']:
                res[top.id] = top.flat_cons_m2
            elif top.type in ['shop', 'industrial_unit', 'hotel_industry', 'premise']:
                res[top.id] = top.ground_cons_m2
            elif top.type in ['office','premise-office']:
                res[top.id] = top.office_cons_m2
            elif top.type in ['chalet','house']:
                res[top.id] = top.chalet_cons_m2
            elif top.type in ['land']:
                res[top.id] = top.land_cons_m2
            else:
                res[top.id] = 0
        return res
    
    def _m2_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        menu = self.pool.get('ir.ui.menu').browse(cr,uid,context['active_id'])
        operator = args[0][1]
        value = args[0][2]
        top_obj = self.pool.get('real.state.top')
        top_div_obj = self.pool.get('real.state.top.subsivision')
        if menu.action.domain:
            if menu.action.domain.find('flat') >= 0: 
               top_ids = top_obj.search(cr, uid, 
                                        [('flat_usage_m2',operator,value)])
            elif menu.action.domain.find('shop') >= 0 or menu.action.domain.find('industrial_unit') >= 0 or menu.action.domain.find('hotel_industry') >= 0 or menu.action.domain.find('premise') >= 0:
               top_ids = top_obj.search(cr, uid, [
                           ('ground_m2',operator,value),
                           ])
               sub_ids = top_div_obj.search(cr, uid, [('m2',operator,value)])
               for sub_id in sub_ids:
                   sub = top_div_obj.browse(cr, uid, sub_id)
                   if sub.top_id.id not in top_ids:
                       top_ids.append(sub.top_id.id)
            elif menu.action.domain.find('office') >= 0 or menu.action.domain.find('premise-office') >=0:
               top_ids = top_obj.search(cr, uid, [
                           ('office_m2',operator,value),
                           ])
               sub_ids = top_div_obj.search(cr, uid, [('m2',operator,value)])
               for sub_id in sub_ids:
                   sub = top_div_obj.browse(cr, uid, sub_id)
                   if sub.top_id.id not in top_ids:
                       top_ids.append(sub.top_id.id)
            elif menu.action.domain.find('chalet') >= 0 or menu.action.domain.find('house') >=0:
               top_ids = top_obj.search(cr, uid, [
                           ('chalet_usage_m2',operator,value),
                           ])
            elif menu.action.domain.find('land') >= 0:
               top_ids = top_obj.search(cr, uid, [
                           ('land_m2',operator,value),
                           ])
        else:
            return []
        if len(top_ids) > 0:
            return [('id','in', top_ids)]
        return []
    
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
 
    def operation_getselectionval(self, cr, uid, ids):
        info = self.browse(cr, uid, ids)
        for operationtuple in self.OPERATIONS:
            if info[0].operation == operationtuple[0]:
               return operationtuple[1]

    _columns = {
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Last Write Date', readonly=True),
        'name': fields.char('Reference', size=64, select=True, readonly=True),
        'address': fields.char('Address', size=256, required=True),
        'stair': fields.char('Stair', size=256),
        'number': fields.char('Number', size=64, select=True),
        'floor': fields.char('Floor', size=64, select=True),
        'type': fields.selection(TYPES, 'Type', required=True, select=True),
        'zone': fields.many2one('real.state.zone','Zone', required=True, 
                                select=True),
        'city_id': fields.many2one(
            'city.city', 'Location', required=True,
            help='Use the name or the zip to search the location'),
        'partner_id': fields.many2one('res.partner',
            'Owner', 
            select=True, 
            domain= [('real_state_type','=','owner')]),
        'operation': fields.selection(OPERATIONS, 'Operation', required=True, 
                                      select=True),
        'date': fields.date('Date', required=True),
        'updated_date': fields.date('Updated Date'),
        'number_keys': fields.char('Number of Keys', size=256),
        'exclusive': fields.boolean('Exclusive'),
        'exclusive_date': fields.date('Exclusive Date'),
        'agreements': fields.one2many('rental.agreement', 'top_id', 'Rental Agreements'),
        'attachments_url': fields.function(_get_mount_point, method=True, store=False, type='char', size=1024, string='Attachments URL'),
        # Common information
        'sale_price': fields.float('Sale Price'),
        'rent_price': fields.float('Rent Price'),
        'homeowners_expenses': fields.char('Homeowners Expenses',size=256),
        'homeowners_expenses_included': fields.boolean('Included'),
        'deposit': fields.char('Deposit', size=256),
        'note': fields.text('Notes'),
        'available': fields.boolean('Available'),
        'subtype': fields.many2one('real.state.subtype','Subtype', select=True),
        'energy_efficiency': fields.selection(ENERGY_EFFICIENCY, 
                                              'Energy Efficiency', 
                                              required=False),
        'energy_date': fields.date('Date Energy Efficiency'),
        'energy_emission': fields.integer('Energy Emission'),
        'energy_number': fields.integer('Energy Number'),
        'energy_doc': fields.binary('Energy Certificate'),
        'retribution': fields.char('Retribution', size=256),
        'buyer_id': fields.many2one('res.partner',
            'Buyer',
            domain= [('real_state_type','=','buyer')]),
        'm2': fields.function(_m2_get, method=True, type='float', string='M2',
                              store=False, fnct_search=_m2_search),
        'cons_m2': fields.function(_cons_m2_get, method=True, type='float',
                                   string='Constructed M2', store=False),
        'subdivision_ids':fields.one2many('real.state.top.subsivision', 
                                          'top_id', 'Subdivisions', 
                                          required=False), 
        # Flat, Chalet, Town House information
        'kitchen': fields.integer('Kitchen'),
        'kitchen_description': fields.char('Kitchen Description', size=256),
        'hall': fields.integer('Hall'),
        'hall_description': fields.char('Hall Description', size=256),
        'rooms': fields.integer('Rooms'),
        'room_description': fields.char('Room Description', size=256),
        'bathroom': fields.integer('Bathroom'),
        'bath_description': fields.char('Bathroom Description', size=256),
        'toilet': fields.integer('Toilet'),
        'toilet_description': fields.char('Bathroom Description', size=256),
        'orientation': fields.selection(ORIENTATION, 'Orientation'),
        'parking': fields.integer('Parking'),
        'parking_description': fields.char('Parking Description', size=256),
        'box_room': fields.integer('Box Room'),
        'box_room_description': fields.char('Box Room Description', size=256),
        'outside': fields.boolean('Outside'),
        'balcony': fields.char('Balcony', size=256),
        'note_flat': fields.text('Notes'),
        # Rent Flat, Chalet or Town house
        'bedrooms': fields.integer('Bedrooms'),
        'built_in_closet': fields.integer('Built-in Closet'),
        'furnished': fields.selection(FURNISHED, 'Furnished'),
        'furnished_description': fields.char('Furnished Description', size=256),
        # Suppliers
        'administrator': fields.char('Administrator',size=256),
        'administrator_phone': fields.char('Telephone',size=256),
        'email': fields.char('E-Mail', size=256),
        'website': fields.char('Website',size=256, help="Website of Administrator"),
        'light_ref': fields.char('Light Reference',size=256),
        'gas_ref': fields.char('Gas Reference',size=256),
        'aqua_ref': fields.char('Aqua Reference',size=256),
        # Only Flat.
        'flat_usage_m2': fields.float('Usage M2'),
        'flat_cons_m2': fields.float('Constructed M2'),
        'elevator': fields.boolean('Elevator'),
        'flat_heating': fields.many2one('real.state.heating','Heating'),
        'flat_hotwater': fields.many2one('real.state.hotwater','Hot Water'),
        'students': fields.boolean('Students'),
        # Only Chalet, Town House
        'chalet_usage_m2': fields.float('Usage M2'),
        'chalet_cons_m2': fields.float('Usage M2'),
        'plot_m2': fields.float('Plot M2'),
        'chalet_basement': fields.float('Basement'),
        'chalet_ground': fields.float('Ground'),
        'first_floor': fields.float('First Floor'),
        'second_floor': fields.float('Second Floor'),
        'garden_m2': fields.float('Garden M2'),
        'swimming_pool': fields.boolean('Swimming Pool'),
        'floor_number': fields.integer('Floor Number'),
        'chalet_heating': fields.many2one('real.state.heating','Heating'),
        'chalet_hotwater': fields.many2one('real.state.hotwater','Hot Water'),
        # Industrial Unit information
        'ground_m2': fields.float('Ground M2'),
        'ground_cons_m2': fields.float('Constructed M2'),
        'mezzanine_m2': fields.float('Mezzanine M2'),
        'basement_m2': fields.float('Basement M2'),
        'open_field_m2': fields.float('Open Field M2'),
        'height': fields.float('Height'),
        'electricity': fields.boolean('Eletricity'),
        'triphase': fields.boolean('Triphase'),
        'locker_room': fields.integer('Locker Room'),
        'offices': fields.integer('Offices'),
        'fire_fighting': fields.char('Fire-Fighting',size=256),
        'gantry_crane': fields.char('Gantry Crane',size=256),
        'shop_window': fields.char('Shop Window',size=256),
        'industrial_toilet': fields.integer('Toilet'),
        'industrial_prepared': fields.boolean('Prepared'),
        #Office information
        'office_m2': fields.float('Office M2'),
        'office_cons_m2': fields.float('Usage Office M2'),
        'office_electricity': fields.boolean('Eletricity'),
        'office_toilets': fields.char('Toilets',size=256),
        'office_outside': fields.boolean('Outside'),
        'office_elevator': fields.boolean('Elevator'),
        'office_heating': fields.many2one('real.state.heating','Heating'),
        'office_air_conditioning': fields.char('Air Conditioning',size=256),
        'structural_barriers': fields.boolean('Structural Barriers'),
        'office_parking': fields.char('Parking',size=256),
        'office_boxroom': fields.char('Box Room',size=256),
        #Shop and Premise Information
        'shop_electricity': fields.boolean('Eletricity'),
        'shop_toilet': fields.integer('Toilet'),
        'shop_facade': fields.char('Facade',size=256),
        'shop_heating': fields.many2one('real.state.heating','Heating'),
        'shop_air_conditioning': fields.boolean('Air Conditioning'),
        'shop_prepared': fields.boolean('Prepared'),
        #Hotel industry
        'fumes_vent': fields.boolean('Fumes Vent'),
        #Land
        'land_m2': fields.float('Land M2'),
        'land_cons_m2': fields.float('Usage Land M2'),
        'land_type': fields.many2one('real.state.land.type','Land Type'),
        'land_state': fields.many2one('real.state.land.state','Land State'),
    }
     
    _defaults = {
        'type': 'unlimited',
        'operation': 'sale',
        'available': lambda *a: 1,
        'energy_efficiency': 'in_process',
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'real.state.top')
        res = super(real_state_top, self).create(cr, uid, vals, context)
        return res
    
    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids):
            address = r['name']+'-'+r['address']
            if r['number'] != False: 
                address +=' '+r['number']            
            if r['floor'] != False: 
                address +=','+r['floor']           
            if r['stair'] != False: 
                address +=' '+r['stair']
            res.append((r['id'], address))
        return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('address', operator, name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
     
real_state_top()