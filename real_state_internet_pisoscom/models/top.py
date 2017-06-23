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

class real_state_top(models.Model):
    _inherit = 'real.state.top'
    
    @api.multi
    def _get_pisoscom_operacion(self):
        for top in self:
            value = 0
            if top.operation=='sale' or top.operation=='sale_rent':
                value = 4
            if top.operation=='rent' or top.operation=='rent_sale_option':
                value = 3
            if top.operation=='transfer':
                value = 5
            top.pisoscom_operacion = value
    
    @api.multi
    def _get_pisoscom_precio(self):
        for top in self:
            value = 0
            if top.operation=='sale' or top.operation=='sale_rent':
                value = top.sale_price
            if top.operation=='rent' or top.operation=='rent_sale_option':
                value = top.rent_price
            if top.operation=='transfer':
                value = top.sale_price
            top.pisoscom_precio = int(value)
    
    @api.multi
    def _get_pisoscom_garaje(self):
        for top in self:
            value = '0'
            if top.parking > 0 or top.office_parking > 0:
                value = '1'
            top.pisoscom_garaje = value
    
    @api.multi
    def _get_pisoscom_heating(self):
        for top in self:
            value = '0'
            if (top.flat_heating != False or top.chalet_heating != False 
                or top.office_heating != False or top.shop_heating != False):
                value = '1'
            top.pisoscom_heating = value
    
    @api.multi
    def _get_pisoscom_air(self):
        for top in self:
            value = '0'
            if (top.office_air_conditioning != False or top.shop_air_conditioning != False):
                value = '1'
            top.pisoscom_air = value

    @api.multi
    def _get_pisoscom_furnished(self):
        for top in self:
            value = '0'
            if top.furnished == 'no':
                value = '0'
            else:
                value = '1'
            top.pisoscom_furnished = value

    @api.multi
    @api.onchange('pisoscom')
    def onchange_pisoscom(self):
        pisoscom_tops = self.search([('pisoscom','=',True),
                                    ('available','=',True)])
        
        user  = self.env.user
        
        if len(pisoscom_tops) >= user.company_id.pisoscom:
            raise except_orm(_('Limite excedido!'),
                _('Ha superado el limite de Pisos.com'))
        
        return True
    
    
    @api.multi
    def xml_pisoscom(self):
        
        dominio = self.env.user.company_id
        
        raiz = etree.Element('Publicacion')
        table = etree.SubElement(raiz, 'Table')
        table.attrib['Name'] = 'Inmuebles'
        for top in self.search([('pisoscom','=',True),
                                    ('available','=',True)]):
            inmueble = etree.SubElement(table, 'Inmueble')
            IdInmobiliariaExterna = etree.SubElement(inmueble, 'IdInmobiliariaExterna')
            IdInmobiliariaExterna.text = 'InmobiliariaUrbasa'
            IdPisoExterno = etree.SubElement(inmueble, 'IdPisoExterno')
            IdPisoExterno.text = top.name or ''
            FechaHoraModificado = etree.SubElement(inmueble, 'FechaHoraModificado')
            FechaHoraModificado.text = top.write_date or ''
            TipoInmueble = etree.SubElement(inmueble, 'TipoInmueble')
            TipoInmueble.text = top.pisoscom_type or ''
            TipoOperacion = etree.SubElement(inmueble, 'TipoOperacion')
            TipoOperacion.text = top.pisoscom_operacion or ''
            PrecioEur = etree.SubElement(inmueble, 'PrecioEur')
            PrecioEur.text = top.pisoscom_precio or ''
            NombrePoblacion = etree.SubElement(inmueble, 'NombrePoblacion')
            NombrePoblacion.text = smart_unicode(top.city_id.city or '')
            CodigoPostal = etree.SubElement(inmueble, 'CodigoPostal')
            CodigoPostal.text = top.city_id.name or ''
            Situacion1 = etree.SubElement(inmueble, 'Situacion1')
            Situacion1.text = smart_unicode(top.zone.name or '')
            SuperficieUtil = etree.SubElement(inmueble, 'SuperficieUtil')
            SuperficieUtil.text = str(top.m2 or '')
            HabitacionesDobles = etree.SubElement(inmueble, 'HabitacionesDobles')
            HabitacionesDobles.text = str(top.pisoscom_number_doblehab or '')
            HabitacionesSimples = etree.SubElement(inmueble, 'HabitacionesSimples')
            HabitacionesSimples.text = str(top.pisoscom_number_indhab or '')
            BanosCompletos = etree.SubElement(inmueble, 'BanosCompletos')
            BanosCompletos.text = str(top.pisoscom_number_banocomp or '')
            BanosAuxiliares = etree.SubElement(inmueble, 'BanosAuxiliares')
            BanosAuxiliares.text = str(top.pisoscom_number_banoaux or '')
            Expediente = etree.SubElement(inmueble, 'Expediente')
            Expediente.text = top.name or ''
            Email = etree.SubElement(inmueble, 'Email')
            Email.text = 'alquiler@inmobiliariaurbasa.com'
            Telefono = etree.SubElement(inmueble, 'Telefono')
            Telefono.text = '948211314'
            Descripcion = etree.SubElement(inmueble, 'Descripcion')
            Descripcion.text = smart_unicode(top.internet_description or '')
            Fotos = etree.SubElement(inmueble, 'Fotos')
            if top.image_ids != False:
                for image in top.image_ids:
                    Foto = etree.SubElement(Fotos, 'Foto'+str(image.sequence))
                    Foto.text = dominio.domain + 'website/image/base_multi_image.image/' + str(image.id) + '/file_db_store'
            NombreCalle = etree.SubElement(inmueble, 'NombreCalle')
            NombreCalle.text = smart_unicode(top.address or '')
            NumeroCalle = etree.SubElement(inmueble, 'NumeroCalle')
            NumeroCalle.text = top.number or ''
            Escalera = etree.SubElement(inmueble, 'Escalera')
            Escalera.text = top.stair or ''
            Piso = etree.SubElement(inmueble, 'Piso')
            Piso.text = top.floor or ''
            Cocina_tiene = etree.SubElement(inmueble, 'Cocina_tiene')
            if top.kitchen > 0:
                Cocina_tiene.text = str(1)
            else:
                Cocina_tiene.text = str(0)
            Cocina_comentario = etree.SubElement(inmueble, 'Cocina_comentario')
            Cocina_comentario.text = smart_unicode(top.kitchen_description or '')
            Trastero_tiene = etree.SubElement(inmueble, 'Trastero_tiene')
            if top.box_room > 0:
                Trastero_tiene.text = str(1)
            else:
                Trastero_tiene.text = str(0)
            Trastero_comentario = etree.SubElement(inmueble, 'Trastero_comentario')
            Trastero_comentario.text = smart_unicode(top.box_room_description or '')
            Garaje_tiene = etree.SubElement(inmueble, 'Garaje_tiene')
            Garaje_tiene.text = top.pisoscom_garaje or ''
            Garaje_comentario = etree.SubElement(inmueble, 'Garaje_comentario')
            Garaje_comentario.text = smart_unicode(top.parking_description or '')
            Ascensor_tiene = etree.SubElement(inmueble, 'Ascensor_tiene')
            if top.elevator:
                Ascensor_tiene.text = str(1)
            else:
                Ascensor_tiene.text = str(0)
            Ascensor_comentario = etree.SubElement(inmueble, 'Ascensor_comentario')
            Ascensor_comentario.text = ''
            Balcon_tiene = etree.SubElement(inmueble, 'Balcon_tiene')
            Balcon_tiene.text = top.balcony or ''
            Balcon_comentario = etree.SubElement(inmueble, 'Balcon_comentario')
            Balcon_comentario.text = ''
            Terraza_tiene = etree.SubElement(inmueble, 'Terraza_tiene')
            Terraza_tiene.text = top.balcony or ''
            Terraza_comentario = etree.SubElement(inmueble, 'Terraza_comentario')
            Terraza_comentario.text = ''
            Jardin_tiene = etree.SubElement(inmueble, 'Jardin_tiene')
            if top.garden_m2 > 0:
                Jardin_tiene.text = str(1)
            else:
                Jardin_tiene.text = str(0)
            Jardin_comentario = etree.SubElement(inmueble, 'Jardin_comentario')
            Jardin_comentario.text = ''
            Piscina_tiene = etree.SubElement(inmueble, 'Piscina_tiene')
            if top.swimming_pool:
                Piscina_tiene.text = str(1)
            else:
                Piscina_tiene.text = str(0)
            Piscina_comentario = etree.SubElement(inmueble, 'Piscina_comentario')
            Piscina_comentario.text = ''
            Calefaccion_tiene = etree.SubElement(inmueble, 'Calefaccion_tiene')
            Calefaccion_tiene.text = top.pisoscom_heating or ''
            Calefaccion_comentario = etree.SubElement(inmueble, 'Calefaccion_comentario')
            Calefaccion_comentario.text = ''
            AireAcondicionado_tiene = etree.SubElement(inmueble, 'AireAcondicionado_tiene')
            AireAcondicionado_tiene.text = top.pisoscom_air or ''
            AireAcondicionado_comentario = etree.SubElement(inmueble, 'AireAcondicionado_comentario')
            AireAcondicionado_comentario.text = ''
            Amueblado_tiene = etree.SubElement(inmueble, 'Amueblado_tiene')
            Amueblado_tiene.text = top.pisoscom_furnished or ''
            Amueblado_comentario = etree.SubElement(inmueble, 'Amueblado_comentario')
            Amueblado_comentario.text = smart_unicode(top.furnished_description or '')
            SuministroAgua_tiene = etree.SubElement(inmueble, 'SuministroAgua_tiene')
            SuministroAgua_tiene.text = str(1)
            SuministroElectrico_tiene = etree.SubElement(inmueble, 'SuministroElectrico_tiene')
            SuministroElectrico_tiene.text = str(1)
            Grua_tiene = etree.SubElement(inmueble, 'Grua_tiene')
            if top.gantry_crane != False:
                Grua_tiene.text = str(1)
            else:
                Grua_tiene.text = str(0)
            Grua_comentario = etree.SubElement(inmueble, 'Grua_comentario')
            Grua_comentario.text = ''
            Oficina_tiene = etree.SubElement(inmueble, 'Oficina_tiene')
            if top.offices > 0:
                Oficina_tiene.text = str(1)
            else:
                Oficina_tiene.text = str(0)
            Oficina_comentario = etree.SubElement(inmueble, 'Oficina_comentario')
            Oficina_comentario.text = ''
            SalidaHumos_tiene = etree.SubElement(inmueble, 'SalidaHumos_tiene')
            if top.fumes_vent:
                SalidaHumos_tiene.text = str(1)
            else:
                SalidaHumos_tiene.text = str(0)
            SalidaHumos_comentario = etree.SubElement(inmueble, 'SalidaHumos_comentario')
            SalidaHumos_comentario.text = ''
            SalidaAntincendios_tiene = etree.SubElement(inmueble, 'SalidaAntincendios_tiene')
            if top.fire_fighting != False:
                SalidaAntincendios_tiene.text = str(1)
            else:
                SalidaAntincendios_tiene.text = str(0)
            SalidaAntincendios_comentario = etree.SubElement(inmueble, 'SalidaAntincendios_comentario')
            SalidaAntincendios_comentario.text = ''
            Escaparate_tiene = etree.SubElement(inmueble, 'Escaparate_tiene')
            if top.shop_window != False:
                Escaparate_tiene.text = str(1)
            else:
                Escaparate_tiene.text = str(0)
            Escaparate_comentario = etree.SubElement(inmueble, 'Escaparate_comentario')
            Escaparate_comentario.text = ''
            Vestuarios_tiene = etree.SubElement(inmueble, 'Vestuarios_tiene')
            if top.locker_room != False:
                Vestuarios_tiene.text = str(1)
            else:
                Vestuarios_tiene.text = str(0)
            Vestuarios_comentario = etree.SubElement(inmueble, 'Vestuarios_comentario')
            Vestuarios_comentario.text = ''
            CertificacionEnergetica_tiene = etree.SubElement(inmueble, 'CertificacionEnergetica_tiene')
            if top.energy_efficiency not in ['in_process', 'exempt', 'yes']:
                CertificacionEnergetica_tiene.text = str(1)
            else:
                CertificacionEnergetica_tiene.text = str(0)
            CertificacionEnergetica_comentario = etree.SubElement(inmueble, 'CertificacionEnergetica_comentario')
            if top.energy_efficiency not in ['in_process', 'exempt', 'yes']:
                CertificacionEnergetica_comentario.text = top.energy_efficiency or ''
            else:
                CertificacionEnergetica_comentario.text = ''
            PrestacionEnergetica_tiene = etree.SubElement(inmueble, 'PrestacionEnergetica_tiene')
            if top.energy_efficiency not in ['in_process', 'exempt', 'yes']:
                PrestacionEnergetica_tiene.text = str(1)
            else:
                PrestacionEnergetica_tiene.text = str(0)
            PrestacionEnergetica_comentario = etree.SubElement(inmueble, 'PrestacionEnergetica_comentario')
            PrestacionEnergetica_comentario.text = str(top.energy_number or '')
            CalificacionEmisionesEnergeticas = etree.SubElement(inmueble, 'CalificacionEmisionesEnergeticas')
            CalificacionEmisionesEnergeticas.text = ''
            EmisionesEnergeticas = etree.SubElement(inmueble, 'EmisionesEnergeticas')
            EmisionesEnergeticas.text = str(top.energy_emission or '')
            
        prueba = etree.tostring(raiz, encoding='UTF-8',
            xml_declaration=True)
        return prueba

    TYPE = [
            ('Pisos','Pisos'),
            ('Casas','Casas'),
            ('Locales','Locales'),
            ('Oficinas','Oficinas'),
            ('Naves','Naves'),
            ('Terrenos','Terrenos'),
            ('Garajes','Garajes'),
            ('Trasteros','Trasteros'),
            ('Habitaciones','Habitaciones'),
             ]
    
    pisoscom = fields.Boolean('Publicado en pisos.com')
    pisoscom_type = fields.Selection(TYPE, 'Tipo en pisos.com', 
                                              select=True, readonly=False)
    pisoscom_operacion = fields.Char(compute='_get_pisoscom_operacion', 
                                           method=True, store=False)
    pisoscom_precio = fields.Char(compute='_get_pisoscom_precio', method=True, 
                                           store=False)
    pisoscom_number_doblehab = fields.Integer('Nº Habitaciones dobles')
    pisoscom_number_indhab = fields.Integer('Nº Habitaciones simples')
    pisoscom_number_banocomp = fields.Integer('Nº Baños completos')
    pisoscom_number_banoaux = fields.Integer('Nº Baños simples')
    pisoscom_garaje = fields.Char(compute='_get_pisoscom_garaje', method=True, 
                                           store=False)
    pisoscom_heating = fields.Char(compute='_get_pisoscom_heating', method=True, 
                                           store=False)
    pisoscom_air = fields.Char(compute='_get_pisoscom_air', method=True, 
                                           store=False)
    pisoscom_furnished = fields.Char(compute='_get_pisoscom_furnished', 
                                              method=True, store=False)
    
    
