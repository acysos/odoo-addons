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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from lxml import etree
from django.utils.encoding import smart_str, smart_unicode
import code
import logging

_logger = logging.getLogger(__name__)


class real_estate_heating(models.Model):
    _inherit = 'real.estate.heating'
    
    idealistacom_type = fields.Selection([
            ('0','Desconocido'),
            ('1','No disponible'),
            ('2','Independiente'),
            ('3','Central'),
            ('4','Preinstalación'),
             ],    'Tipo Idealista', select=True, readonly=False)
    
    

class real_estate_hotwater(models.Model):
    _inherit = 'real.estate.hotwater'
    
    idealistacom_type = fields.Selection([
            ('0','Desconocido'),
            ('1','No disponible'),
            ('2','Independiente'),
            ('3','Central'),
            ('4','Preinstalación'),
             ],    'Tipo Idealista', select=True, readonly=False)
    

class real_estate_top(models.Model):
    _inherit = 'real.estate.top'
    
    @api.multi
    def _get_idealistacom_operacion(self):
        for top in self:
            value = ''
            if top.operation=='sale' or top.operation=='sale_rent':
                value = 'sale'
            if top.operation=='rent':
                value = 'rent'
            if top.operation=='rent_sale_option':
                value = 'renttoown'
            top.idealistacom_operacion = value
    
    @api.multi
    def _get_idealistacom_air(self):
        for top in self:
            value = '0'
            if (top.office_air_conditioning != False or top.shop_air_conditioning != False):
                value = '2'
            top.idealistacom_air = value
    
    @api.multi
    def _get_idealistacom_heating(self):
        for top in self:
            value = ''
            if top.type=='flat':
                value = top.flat_heating.idealistacom_type
            elif top.type=='shop':
                value = top.shop_heating.idealistacom_type
            elif top.type=='premise':
                value = top.shop_heating.idealistacom_type
            elif top.type=='chalet':
                value = top.chalet_heating.idealistacom_type
            elif top.type=='house':
                value = top.chalet_heating.idealistacom_type
            elif top.type=='office':
                value = top.office_heating.idealistacom_type
            top.idealistacom_heating = value
    
    @api.multi        
    def _get_idealistacom_hotwater(self):
        for top in self:
            value = ''
            if top.type=='flat':
                value = top.flat_hotwater.idealistacom_type
            elif top.type=='chalet':
                value = top.chalet_hotwater.idealistacom_type
            elif top.type=='house':
                value = top.chalet_hotwater.idealistacom_type
            top.idealistacom_hotwater = value
    
    @api.multi
    def _get_idealistacom_orienta(self):
        for top in self:
            value = ''
            if top.orientation=='all':
                value = '0'
            if top.orientation=='north':
                value = '1'
            if top.orientation=='northeast':
                value = '2'
            if top.orientation=='east':
                value = '3'
            if top.orientation=='southeast':
                value = '4'
            if top.orientation=='south':
                value = '5'
            if top.orientation=='southwest':
                value = '6'
            if top.orientation=='west':
                value = '7'
            if top.orientation=='northwest':
                value = '8'  
            top.idealistacom_orienta = value      
    
    @api.multi
    def _get_idealistacom_energyef(self):
        for top in self:
            value = '0'
            if top.energy_efficiency=='in_process':
                value = '0'
            if top.energy_efficiency=='exempt':
                value = '1'
            if top.energy_efficiency=='a':
                value = '2'
            if top.energy_efficiency=='b':
                value = '3'
            if top.energy_efficiency=='c':
                value = '4'
            if top.energy_efficiency=='d':
                value = '5'
            if top.energy_efficiency=='e':
                value = '6'
            if top.energy_efficiency=='f':
                value = '7'
            if top.energy_efficiency=='g':
                value = '8'
            if top.energy_efficiency=='yes':
                value = '0'
            top.idealistacom_energyef = value
    
    @api.multi
    def _get_idealistacom_furnished(self):
        for top in self:
            value = '0'
            if top.furnished=='yes':
                value = '3'
            if top.furnished=='half':
                value = '3'
            if top.furnished=='no':
                value = '1'
            top.idealistacom_furnished = value
            
    @api.multi
    def _get_idealistacom_state(self):
        for top in self:
            value = ''
            if top.top_state=='0':
                value = '0'
            if top.top_state=='1' or top.top_state == '3':
                value = '1'
            if top.top_state=='2':
                value = '3'
            if top.top_state=='4':
                value = '2'    
            top.idealistacom_state = value    
            
    @api.multi
    def _get_idealistacom_bathroom(self):
        for top in self:
            value = ''
            if top.type=='flat':
                value = top.bathroom
            elif top.type=='shop':
                value = top.shop_heating.idealistacom_type
            elif top.type=='premise':
                value = top.shop_toilet
            elif top.type=='chalet':
                value = top.bathroom
            elif top.type=='house':
                value = top.bathroom
            elif top.type=='office':
                value = top.office_toilets
            elif top.type=='industrial_unit':
                value = top.industrial_toilet
            top.idealistacom_bathroom = value
            
    @api.multi
    def _get_idealistacom_type(self):
        for top in self:
            value = ''
            if top.type=='flat':
                value = 'flat'
            elif top.type=='shop':
                value = top.shop_heating.idealistacom_type
            elif top.type=='premise':
                value = 'premise'
            elif top.type=='chalet':
                value = 'house'
            elif top.type=='house':
                value = 'countryhouse'
            elif top.type=='office':
                value = 'office'
            elif top.type=='industrial_unit':
                value = 'premise'
            elif top.type=='hotel_industry':
                value = 'premise'
            elif top.type=='parking':
                value = 'garage'        
            top.idealistacom_type = value
    
    @api.multi
    def _get_idealistacom_outside(self):
        for top in self:
            value = '2'
            if top.outside or top.office_outside:
                value = '1'
            top.idealistacom_outside = value
    
    @api.multi
    @api.onchange('idealista')
    def onchange_idealista(self):
        idealista_tops = self.search([('idealista','=',True),
                                    ('available','=',True)])
        
        user  = self.env.user
        
        if len(idealista_tops) >= user.company_id.idealista:
            raise except_orm(_('Limite excedido!'),
                _('Ha superado el limite de Idealista'))
        
        return True
    
    @api.multi
    def xml_idealista(self):
        
         company = self.env.user.company_id
        
         raiz = etree.Element('clients')
         cliente = etree.SubElement(raiz, 'client')
         aggregator = etree.SubElement(cliente, 'aggregator')
         aggregator.text = company.idealista_aggregator or ''
         code = etree.SubElement(cliente, 'code')
         code.text = company.idealista_code or ''
         contact = etree.SubElement(cliente, 'contact')
         name = etree.SubElement(contact, 'name')
         name.text = company.name
         email = etree.SubElement(contact, 'email')
         email.text = company.email
         phones = etree.SubElement(contact, 'phones')
         phone = etree.SubElement(phones, 'phone')
         prefix = etree.SubElement(phone, 'prefix')
         prefix.text = company.idealista_prefix or ''
         number = etree.SubElement(phone, 'number')
         number.text = company.phone
         availabilityHour = etree.SubElement(phone, 'availabilityHour')
         availabilityHour.text = '1'
         secondhandlisting = etree.SubElement(cliente, 'secondhandListing')
         for top in self.search([('idealista','=',True),
                                    ('available','=',True)]):
             property = etree.SubElement(secondhandlisting, 'property')
             operation = etree.SubElement(property, 'operation')
             operation.attrib["type"] = top.idealistacom_operacion or ''
             if top.operation=='sale' or top.operation=='sale_rent':
                 price = etree.SubElement(operation, 'price')
                 price.text= str(top.sale_price or '')
             if top.operation=='rent':
                 price = etree.SubElement(operation, 'price')
                 price.text= str(top.rent_price or '')
             if top.operation=='rent_sale_option':
                 price = etree.SubElement(operation, 'price')
                 price.text= str(top.rent_price or '')
                 salePrice = etree.SubElement(operation, 'salePrice')
                 salePrice.text= str(top.sale_price or '')
             code = etree.SubElement(property, 'code')
             code.text = top.name or ''
             reference = etree.SubElement(property, 'reference')
             reference.text = top.name or ''
             scope = etree.SubElement(property, 'scope')
             scope.text = str(1)
             address = etree.SubElement(property, 'address')
             visibility = etree.SubElement(address, 'visibility')
             visibility.text = str(2)
             country = etree.SubElement(address, 'country')
             country.text = top.city_id.country_id.code or ''
             streetName = etree.SubElement(address, 'streetName')
             streetName.text = smart_unicode(top.address or '')
             streetNumber = etree.SubElement(address, 'streetNumber')
             streetNumber.text = top.number or ''
             floor = etree.SubElement(address, 'floor')
             floor.text = top.floor or ''
             block = etree.SubElement(address, 'block')
             block.text = ''
             stair = etree.SubElement(address, 'stair')
             stair.text = top.stair or ''
             door = etree.SubElement(address, 'door')
             door.text = top.door or ''
             postalcode = etree.SubElement(address, 'postalcode')
             postalcode.text = top.city_id.name or ''
             cityName = etree.SubElement(address, 'cityName')
             cityName.text = top.city_id.city or ''
             coordinates = etree.SubElement(address, 'coordinates')
             precision = etree.SubElement(coordinates, 'precision')
             precision.text = str(2)
             latitude = etree.SubElement(coordinates, 'latitude')
             latitude.text = top.latitude or ''
             longitude = etree.SubElement(coordinates, 'longitude')
             longitude.text = top.longitude or ''
             links = etree.SubElement(property, 'links')
             link = etree.SubElement(links, 'link')
             language = etree.SubElement(link, 'language')
             language.text = str(1)
             comment = etree.SubElement(link, 'comment')
             comment.text = ''
             url = etree.SubElement(link, 'url')
             url.text = ''
             descriptions = etree.SubElement(property, 'descriptions')
             description = etree.SubElement(descriptions, 'description')
             language2 = etree.SubElement(description, 'language')
             language2.text = str(1)
             title = etree.SubElement(description, 'title')
             title.text = ''
             comment2 = etree.SubElement(description, 'comment')
             comment2.text = smart_unicode(top.internet_description or '')
             images = etree.SubElement(property, 'images')
             if top.image_ids != False:
                 for image in top.image_ids:
                     imagexml = etree.SubElement(images, 'image')
                     url2 = etree.SubElement(imagexml, 'url')
                     url2.text = 'http://' + company.domain + '/web/binary/saveas?model=base_multi_image.image&field=file_db_store&filename_field=name&id=' + str(image.id)
                     code2 = etree.SubElement(imagexml, 'code')
                     code2.text = str(image.sequence)
             features = etree.SubElement(property, 'features')
             features.attrib['type'] = top.idealistacom_type or ''
             constructedArea = etree.SubElement(features, 'constructedArea')
             constructedArea.text = str(top.cons_m2 or '')
             usableArea = etree.SubElement(features, 'usableArea')
             usableArea.text = str(top.m2 or '')
             plotArea = etree.SubElement(features, 'plotArea')
             plotArea.text = str(top.plot_m2 or '')
             bedrooms = etree.SubElement(features, 'bedrooms')
             bedrooms.text = str(top.rooms or '')
             bathrooms = etree.SubElement(features, 'bathrooms')
             bathrooms.text = top.idealistacom_bathroom or ''
             buildingType = etree.SubElement(features, 'buildingType')
             buildingType.text = top.idealistacom_state or ''
             conditionedAir = etree.SubElement(features, 'conditionedAir')
             conditionedAir.text = top.idealistacom_air or ''
             heatingType = etree.SubElement(features, 'heatingType')
             heatingType.text = top.idealistacom_heating or ''
             hotwaterType = etree.SubElement(features, 'hotwaterType')
             hotwaterType.text = top.idealistacom_hotwater or ''
             orientation = etree.SubElement(features, 'orientation')
             orientation.text = top.idealistacom_orienta or ''
             parkingSpacesInPrice = etree.SubElement(features, 'parkingSpacesInPrice')
             parkingSpacesInPrice.text = str(top.parking or '')
             energyCertification = etree.SubElement(features, 'energyCertification')
             rating = etree.SubElement(energyCertification, 'rating')
             rating.text = top.idealistacom_energyef or ''
             performance = etree.SubElement(energyCertification, 'performance')
             performance.text = str(top.energy_number or '')
             rooms = etree.SubElement(features, 'rooms')
             rooms.text = str(top.rooms or '')
             furniture = etree.SubElement(features, 'furniture')
             furniture.text = top.idealistacom_furnished or ''
             storageRoom = etree.SubElement(features, 'storageRoom')
             if top.box_room > 0:
                 storageRoom.text = 'true'
             else:
                 storageRoom.text = 'false'
             garden = etree.SubElement(features, 'garden')
             if top.garden_m2 > 0:
                 garden.text = 'true'
             else:
                 garden.text = 'false'
             swimming_pool = etree.SubElement(features, 'swimming_pool')
             if top.swimming_pool:
                 swimming_pool.text = 'true'
             else:
                 swimming_pool.text = 'false'
             handicappedAdapted = etree.SubElement(features, 'handicappedAdapted')
             handicappedAdapted.text = 'true'
             balconyNumber = etree.SubElement(features, 'balconyNumber')
             balconyNumber.text = smart_unicode(top.balcony or '')
             windowsLocation = etree.SubElement(features, 'windowsLocation')
             windowsLocation.text = top.idealistacom_outside or ''
             elevator = etree.SubElement(features, 'elevator')
             if top.elevator:
                 elevator.text = 'true'
             else:
                 elevator.text = 'false'
             smokeExtraction = etree.SubElement(features, 'smokeExtraction')
             if top.fumes_vent > 0:
                 smokeExtraction.text = 'true'
             else:
                 smokeExtraction.text = 'false'
             
         prueba = etree.tostring(raiz, encoding='UTF-8',
            xml_declaration=True)
         return prueba
    
    idealista = fields.Boolean('Publicado en idealista.com')
    idealistacom_operacion = fields.Char(compute='_get_idealistacom_operacion', 
                                            method=True, store=False)
    idealistacom_type = fields.Char(compute='_get_idealistacom_type', 
                                            method=True, store=False)
    idealistacom_air = fields.Char(compute='_get_idealistacom_air', 
                                            method=True, store=False)
    idealistacom_heating = fields.Char(compute='_get_idealistacom_heating',
                                            method=True, store=False)
    idealistacom_hotwater = fields.Char(compute='_get_idealistacom_hotwater',
                                            method=True, store=False)
    idealistacom_orienta = fields.Char(compute='_get_idealistacom_orienta',
                                            method=True, store=False)
    idealistacom_energyef = fields.Char(compute='_get_idealistacom_energyef',
                                            method=True, store=False)
    idealistacom_furnished = fields.Char(compute='_get_idealistacom_furnished',
                                            method=True, store=False)
    idealistacom_state = fields.Char(compute='_get_idealistacom_state',
                                            method=True, store=False)
    idealistacom_bathroom = fields.Char(compute='_get_idealistacom_bathroom',
                                            method=True, store=False)
    idealistacom_outside = fields.Char(compute='_get_idealistacom_outside',
                                            method=True, store=False)
    
    
    
    
    