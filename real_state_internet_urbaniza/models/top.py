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
from django.utils.encoding import smart_str, smart_unicode
import datetime
from lxml import etree

class real_state_top(models.Model):
    _inherit = 'real.state.top'

    @api.multi
    def _get_inmoagrupacom_heating(self):
        for top in self:
            value = ''
            if (top.flat_heating != False or top.chalet_heating != False 
                or top.office_heating != False or top.shop_heating != False):
                value = '1'        
            top.inmoagrupacom_heating = value
    
    
    @api.multi
    def _get_inmoagrupacom_capt_date(self):
        for top in self:
            value = ''
            if top.capt_date:
                value = datetime.datetime.strptime(top.capt_date, '%Y-%m-%d').strftime('%d/%m/%Y')            
            top.inmoagrupacom_capt_date = value
    
    @api.multi
    def _get_inmoagrupacom_end_date(self):
        for top in self:
            value = ''
            if top.end_date:
                value = datetime.datetime.strptime(top.end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            top.inmoagrupacom_end_date = value
            
    @api.multi
    def _get_inmoagrupacom_energy_date(self):
        for top in self:
            value = ''
            if top.energy_date:
                value = datetime.datetime.strptime(top.energy_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            top.inmoagrupacom_energy_date = value
            
    
    @api.multi
    def xml_inmoagrupacom(self):
        
        dominio = self.env.user.company_id
        
        raiz = etree.Element('Inmuebles')
        for top in self.search([('inmoagrupacom','=',True),
                                    ('available','=',True)]):
            inmueble = etree.SubElement(raiz, 'inmueble')
            referencia_unica = etree.SubElement(inmueble, 'referencia_unica')
            referencia_unica.text = top.name or ''
            referencia_anunciante = etree.SubElement(inmueble, 'referencia_anunciante')
            referencia_anunciante.text = top.name or ''
            pais = etree.SubElement(inmueble, 'pais')
            pais.text = etree.CDATA(top.city_id.country_id.name or '')
            provincia = etree.SubElement(inmueble, 'provincia')
            provincia.text = etree.CDATA(top.city_id.state_id.name or '')
            poblacion = etree.SubElement(inmueble, 'poblacion')
            poblacion.text = etree.CDATA(top.city_id.city or '')
            zona = etree.SubElement(inmueble, 'zona')
            zona.text = etree.CDATA(top.zone.name or '')
            direccion_visible_01 = etree.SubElement(inmueble, 'direccion_visible_01')
            direccion_visible_01.text = str(1)
            direccion_completa_01 = etree.SubElement(inmueble, 'direccion_completa_01')
            direccion_completa_01.text = str(1)
            direccion_tipo_via = etree.SubElement(inmueble, 'direccion_tipo_via')
            direccion_tipo_via.text = etree.CDATA(top.inmoagrupacom_street_type or '')
            direccion_calle = etree.SubElement(inmueble, 'direccion_calle')
            direccion_calle.text = etree.CDATA(top.address or '')
            direccion_numero = etree.SubElement(inmueble, 'direccion_numero')
            direccion_numero.text = top.number or ''
            direccion_piso = etree.SubElement(inmueble, 'direccion_piso')
            direccion_piso.text = top.inmoagrupacom_piso or ''
            direccion_letra = etree.SubElement(inmueble, 'direccion_letra')
            direccion_letra.text = top.door or ''
            direccion_escalera = etree.SubElement(inmueble, 'direccion_escalera')
            direccion_escalera.text = top.stair or ''
            cp = etree.SubElement(inmueble, 'cp')
            cp.text = top.city_id.name
            tipo = etree.SubElement(inmueble, 'tipo')
            tipo.text = etree.CDATA(top.inmoagrupacom_type or '')
            gestiones = etree.SubElement(inmueble, 'gestiones')
            if top.operation=='sale':
                gestion1 = etree.SubElement(gestiones, 'gestion')
                tipo1 = etree.SubElement(gestion1, 'tipo')
                tipo1.text = etree.CDATA('Venta')
                precio1 = etree.SubElement(gestion1, 'precio')
                precio1.text = str(top.sale_price)
                honorarios_tipo = etree.SubElement(gestion1, 'honorarios_tipo')
                honorarios_tipo.text = str(top.inmoagrupacom_fee_type or '')
                honorarios_agente_captador = etree.SubElement(gestion1, 'honorarios_agente_captador')
                honorarios_agente_captador.text = str(top.inmoagrupacom_fee_captador or '')
                honorarios_agente_colaborador = etree.SubElement(gestion1, 'honorarios_agente_colaborador')
                honorarios_agente_colaborador.text = str(top.inmoagrupacom_fee_colaborador or '')
                comision_referido = etree.SubElement(gestion1, 'comision_referido')
                comision_referido.text = top.inmoagrupacom_commission_refer or ''
            if top.operation=='rent':
                gestion1 = etree.SubElement(gestiones, 'gestion')
                tipo1 = etree.SubElement(gestion1, 'tipo')
                tipo1.text = etree.CDATA('Alquiler')
                precio1 = etree.SubElement(gestion1, 'precio')
                precio1.text = str(top.rent_price)
                honorarios_tipo = etree.SubElement(gestion1, 'honorarios_tipo')
                honorarios_tipo.text = str(top.inmoagrupacom_fee_type or '')
                honorarios_agente_captador = etree.SubElement(gestion1, 'honorarios_agente_captador')
                honorarios_agente_captador.text = str(top.inmoagrupacom_fee_captador or '')
                honorarios_agente_colaborador = etree.SubElement(gestion1, 'honorarios_agente_colaborador')
                honorarios_agente_colaborador.text = str(top.inmoagrupacom_fee_colaborador or '')
                comision_referido = etree.SubElement(gestion1, 'comision_referido')
                comision_referido.text = top.inmoagrupacom_commission_refer or ''
            if top.operation=='sale_rent':
                gestion1 = etree.SubElement(gestiones, 'gestion')
                tipo1 = etree.SubElement(gestion1, 'tipo')
                tipo1.text = etree.CDATA('Venta')
                precio1 = etree.SubElement(gestion1, 'precio')
                precio1.text = str(top.sale_price)
                honorarios_tipo = etree.SubElement(gestion1, 'honorarios_tipo')
                honorarios_tipo.text = str(top.inmoagrupacom_fee_type or '')
                honorarios_agente_captador = etree.SubElement(gestion1, 'honorarios_agente_captador')
                honorarios_agente_captador.text = str(top.inmoagrupacom_fee_captador or '')
                honorarios_agente_colaborador = etree.SubElement(gestion1, 'honorarios_agente_colaborador')
                honorarios_agente_colaborador.text = str(top.inmoagrupacom_fee_colaborador or '')
                comision_referido = etree.SubElement(gestion1, 'comision_referido')
                comision_referido.text = top.inmoagrupacom_commission_refer or ''
                gestion2 = etree.SubElement(gestiones, 'gestion')
                tipo2 = etree.SubElement(gestion2, 'tipo')
                tipo2.text = etree.CDATA('Alquiler')
                precio2 = etree.SubElement(gestion2, 'precio')
                precio2.text = str(top.rent_price)
                honorarios_tipo = etree.SubElement(gestion2, 'honorarios_tipo')
                honorarios_tipo.text = str(top.inmoagrupacom_fee_type or '')
                honorarios_agente_captador = etree.SubElement(gestion2, 'honorarios_agente_captador')
                honorarios_agente_captador.text = str(top.inmoagrupacom_fee_captador or '')
                honorarios_agente_colaborador = etree.SubElement(gestion2, 'honorarios_agente_colaborador')
                honorarios_agente_colaborador.text = str(top.inmoagrupacom_fee_colaborador or '')
                comision_referido = etree.SubElement(gestion2, 'comision_referido')
                comision_referido.text = top.inmoagrupacom_commission_refer or ''
            if top.operation=='rent_sale_option':
                gestion1 = etree.SubElement(gestiones, 'gestion')
                tipo1 = etree.SubElement(gestion1, 'tipo')
                tipo1.text = etree.CDATA('Alquiler con opción a compra')
                precio1 = etree.SubElement(gestion1, 'precio')
                precio1.text = str(top.rent_price)
                honorarios_tipo = etree.SubElement(gestion1, 'honorarios_tipo')
                honorarios_tipo.text = str(top.inmoagrupacom_fee_type or '')
                honorarios_agente_captador = etree.SubElement(gestion1, 'honorarios_agente_captador')
                honorarios_agente_captador.text = str(top.inmoagrupacom_fee_captador or '')
                honorarios_agente_colaborador = etree.SubElement(gestion1, 'honorarios_agente_colaborador')
                honorarios_agente_colaborador.text = str(top.inmoagrupacom_fee_colaborador or '')
                comision_referido = etree.SubElement(gestion1, 'comision_referido')
                comision_referido.text = top.inmoagrupacom_commission_refer or ''
            if top.operation=='transfer':
                gestion1 = etree.SubElement(gestiones, 'gestion')
                tipo1 = etree.SubElement(gestion1, 'tipo')
                tipo1.text = etree.CDATA('Traspaso')
                precio1 = etree.SubElement(gestion1, 'precio')
                precio1.text = str(top.sale_price)
                honorarios_tipo = etree.SubElement(gestion1, 'honorarios_tipo')
                honorarios_tipo.text = str(top.inmoagrupacom_fee_type or '')
                honorarios_agente_captador = etree.SubElement(gestion1, 'honorarios_agente_captador')
                honorarios_agente_captador.text = str(top.inmoagrupacom_fee_captador or '')
                honorarios_agente_colaborador = etree.SubElement(gestion1, 'honorarios_agente_colaborador')
                honorarios_agente_colaborador.text = str(top.inmoagrupacom_fee_colaborador or '')
                comision_referido = etree.SubElement(gestion1, 'comision_referido')
                comision_referido.text = top.inmoagrupacom_commission_refer or ''
            informacion_gestion = etree.SubElement(inmueble, 'informacion_gestion')
            informacion_gestion.text = ''
            n_habitaciones = etree.SubElement(inmueble, 'n_habitaciones')
            n_habitaciones.text = str(top.rooms) or ''
            n_alcobas = etree.SubElement(inmueble, 'n_alcobas')
            n_alcobas.text = ''
            n_banos = etree.SubElement(inmueble, 'n_banos')
            n_banos.text = str(top.bathroom) or ''
            n_aseos = etree.SubElement(inmueble, 'n_aseos')
            n_aseos.text = str(top.toilet) or ''
            m2_utiles = etree.SubElement(inmueble, 'm2_utiles')
            m2_utiles.text = str(top.m2) or ''
            m2_construidos = etree.SubElement(inmueble, 'm2_construidos')
            m2_construidos.text = str(top.cons_m2) or ''
            m2_terreno = etree.SubElement(inmueble, 'm2_terreno')
            m2_terreno.text = str(top.plot_m2) or ''
            latitud = etree.SubElement(inmueble, 'latitud')
            latitud.text = top.latitude or ''
            longitud = etree.SubElement(inmueble, 'longitud')
            longitud.text = top.longitude or ''
            piso_banco_01 = etree.SubElement(inmueble, 'piso_banco_01')
            piso_banco_01.text = top.inmoagrupacom_bank or ''
            vpo_01 = etree.SubElement(inmueble, 'vpo_01')
            vpo_01.text = top.inmoagrupacom_vpo or ''
            posicion_exacta_01 = etree.SubElement(inmueble, 'posicion_exacta_01')
            posicion_exacta_01.text = str(0)
            estado_vivienda = etree.SubElement(inmueble, 'estado_vivienda')
            estado_vivienda.text = top.top_state or ''
            garaje_012 = etree.SubElement(inmueble, 'garaje_012')
            if top.parking > 0:
                garaje_012.text = str(1)
            else:
                garaje_012.text = ''
            calefaccion_01 = etree.SubElement(inmueble, 'calefaccion_01')
            calefaccion_01.text = top.inmoagrupacom_heating or ''
            a_acondicionado_01 = etree.SubElement(inmueble, 'a_acondicionado_01')
            a_acondicionado_01.text = ''
            piscina_01 = etree.SubElement(inmueble, 'piscina_01')
            if top.swimming_pool:
                piscina_01.text = str(1)
            else:
                piscina_01.text = str(0)
            trastero_01 = etree.SubElement(inmueble, 'trastero_01')
            if top.box_room > 0:
                trastero_01.text = str(1)
            else:
                trastero_01.text = ''
            ascensor_01 = etree.SubElement(inmueble, 'ascensor_01')
            if top.elevator:
                ascensor_01.text = str(1)
            else:
                ascensor_01.text = str(0)
            terraza_01 = etree.SubElement(inmueble, 'terraza_01')
            if top.balcony:
                terraza_01.text = str(1)
            else:
                terraza_01.text = str(0)
            amueblado_01 = etree.SubElement(inmueble, 'amueblado_01')
            if top.furnished == 'no':
                amueblado_01.text = ''
            else:
                amueblado_01.text = '1'
            accesible_01 = etree.SubElement(inmueble, 'accesible_01')
            accesible_01.text = ''
            descripcion = etree.SubElement(inmueble, 'descripcion')
            descripcion.text = top.internet_description or ''
            fotos = etree.SubElement(inmueble, 'fotos')
            if top.image_ids != False:
                for image in top.image_ids:
                    foto = etree.SubElement(fotos, 'foto')
                    url_foto = etree.SubElement(foto, 'url_foto')
                    url_foto.text = etree.CDATA(dominio.domain + 'website/image/base_multi_image.image/' + str(image.id) + '/file_db_store')
                    descripcion_foto = etree.SubElement(foto, 'descripcion_foto')
                    descripcion_foto.text = etree.CDATA(str(image.comments or ''))
                    principal_01 = etree.SubElement(foto, 'principal_01')
                    if (image.sequence == 1):
                        principal_01.text = str(1)
                    else:
                        principal_01.text = str(0)
                    tipo_foto = etree.SubElement(foto, 'tipo_foto')
                    tipo_foto.text = str(0)
                    orden_foto = etree.SubElement(foto, 'orden_foto')
                    orden_foto.text = str(image.sequence)
            url_externa = etree.SubElement(inmueble, 'url_externa')
            url_externa.text = ''
            url_doc_exclusividad = etree.SubElement(inmueble, 'url_doc_exclusividad')
            url_doc_exclusividad.text = top.inmoagrupacom_exclusivity_doc_url or ''
            fecha_captacion = etree.SubElement(inmueble, 'fecha_captacion')
            fecha_captacion.text = top.inmoagrupacom_capt_date or ''
            fecha_fin_mandato = etree.SubElement(inmueble, 'fecha_fin_mandato')
            fecha_fin_mandato.text = top.inmoagrupacom_end_date
            eficiencia_energetica_tipo = etree.SubElement(inmueble, 'eficiencia_energetica_tipo')
            if top.energy_efficiency != 'in_process':
                eficiencia_energetica_tipo.text = top.energy_efficiency
            else:
                eficiencia_energetica_tipo.text = 'Tramite'
            eficiencia_energetica_fecvalid = etree.SubElement(inmueble, 'eficiencia_energetica_fecvalid')
            eficiencia_energetica_fecvalid.text = top.inmoagrupacom_energy_date or ''
            eficiencia_energetica_emisiones = etree.SubElement(inmueble, 'eficiencia_energetica_emisiones')
            eficiencia_energetica_emisiones.text = str(top.energy_emission or '')
            eficiencia_energetica_energia = etree.SubElement(inmueble, 'eficiencia_energetica_energia')
            eficiencia_energetica_energia.text = str(top.energy_number or '')
            url_doc_efic_energetica = etree.SubElement(inmueble, 'url_doc_efic_energetica')
            if top.energy_doc:
                url_doc_efic_energetica.text = dominio.domain + 'web/binary/saveas?model=real.state.top&field=energy_doc&filename_field=name&id=' + str(top.id)     
            else:
                url_doc_efic_energetica.text = ''
            sucursal = etree.SubElement(inmueble, 'sucursal')
            nombre_sucursal = etree.SubElement(sucursal, 'nombre_sucursal')
            nombre_sucursal.text = 'Inmobiliaria Urbasa'
            email_sucursal = etree.SubElement(sucursal, 'email_sucursal')
            email_sucursal.text = 'infor@inmobiliariaurbasa.com'
            poblacion_sucursal = etree.SubElement(sucursal, 'poblacion_sucursal')
            poblacion_sucursal.text = 'Pamplona'
            provincia_sucursal = etree.SubElement(sucursal, 'provincia_sucursal')
            provincia_sucursal.text = 'Navarra'
            telefono_sucursal = etree.SubElement(sucursal, 'telefono_sucursal')
            telefono_sucursal.text = '948211314'
            latitud_sucursal = etree.SubElement(sucursal, 'latitud_sucursal')
            longitud_sucursal = etree.SubElement(sucursal, 'longitud_sucursal')            
            
        prueba = etree.tostring(raiz, encoding='ISO-8859-15',
            xml_declaration=True)
        return prueba.decode('ISO-8859-15')
    
    
    FEE_TYPE = [('P','Porcentaje'),
                 ('E','Euros')]
    
    STREET_TYPE = [
            ('Calle','Calle'),
            ('Avenida','Avenida'),
            ('Barrio','Barrio'),
            ('Bulevar','Bulevar'),
            ('Cantón','Cantón'),
            ('Paseo','Paseo'),
            ('Plaza','Plaza'),
            ('Polígono','Polígono'),
            ('Ronda','Ronda'),
            ('Travesía','Travesía'),
             ]
    
    TYPE = [
            ('Apartamento','Apartamento'),
            ('Bajo','Bajo'),
            ('Estudio','Estudio'),
            ('Triplex','Triplex'),
            ('Otro [Pisos]','Otro [Pisos]'),
            ('Loft','Loft'),
            ('Ático','Ático'),
            ('Piso','Piso'),
            ('Duplex','Duplex'),
            ('Casa','Casa'),
            ('Caserio','Caserio'),
            ('Cueva','Cueva'),
            ('Bungalow','Bungalow'),
            ('Masía','Masía'),
            ('Chalet Individual','Chalet Individual'),
            ('Chalet Pareado','Chalet Pareado'),
            ('Chalet Adosado','Chalet Adosado'),
            ('Villa','Villa'),
            ('Casa Prefabricada','Casa Prefabricada'),
            ('Otro [Casas/Chalets]','Otro [Casas/Chalets]'),
            ('Cortijo','Cortijo'),
            ('Casona','Casona'),
            ('Mansión','Mansión'),
            ('Cabaña','Cabaña'),
            ('Oficina','Oficina'),
            ('Almacén','Almacén'),
            ('Nave Industrial','Nave Industrial'),
            ('Otro [Naves]','Otro [Naves]'),
            ('Bar','Bar'),
            ('Restaurante','Restaurante'),
            ('Txoko','Txoko'),
            ('Residencia','Residencia'),
            ('Granja','Granja'),
            ('Otro [Explotaciones]','Otro [Explotaciones]'),
            ('Edificio','Edificio'),
            ('Hostal-Pensión','Hostal-Pensión'),
            ('Peña Gastronómica','Peña Gastronómica'),
            ('Polígono','Polígono'),
            ('Hotel','Hotel'),
            ('Balneario','Balneario'),
            ('Otro [Terrenos]','Otro [Terrenos]'),
            ('Finca Urbanizable','Finca Urbanizable'),
            ('Solar','Solar'),
            ('Finca Rustica','Finca Rustica'),
            ('Finca','Finca'),
            ('Finca Agraria','Finca Agraria'),
            ('Otro [Locales]','Otro [Locales]'),
            ('Garaje','Garaje'),
            ('Trastero','Trastero'),
             ]
    
    YESNO = [('0', 'No'), ('1', 'Si')]

    inmoagrupacom = fields.Boolean('Publicado en inmoagrupa.com')
    inmoagrupacom_street_type = fields.Selection(STREET_TYPE, 
                                 'Tipo de calle', select=True, readonly=False)
    inmoagrupacom_type = fields.Selection(TYPE, 'Tipo en inmoagrupa.com', 
                                              select=True, readonly=False)
    inmoagrupacom_piso = fields.Char('Piso', size=64, 
                                             required=False, readonly=False)
    inmoagrupacom_letra = fields.Char('Letra', size=64, 
                                             required=False, readonly=False)
    inmoagrupacom_latitude = fields.Char('Latitud', size=64, 
                                             required=False, readonly=False)
    inmoagrupacom_longitude = fields.Char('Longitud', size=64, 
                                             required=False, readonly=False)
    inmoagrupacom_fee_type = fields.Selection(FEE_TYPE,'Tipo honarios', 
                                                  select=True, readonly=False)
    inmoagrupacom_fee_captador = fields.Float('Honorarios captador')
    inmoagrupacom_fee_colaborador = fields.Float('Honorarios colaborador')
    inmoagrupacom_commission_refer = fields.Float('Comisión referido')
    inmoagrupacom_bank = fields.Selection(YESNO, 'Piso Banco', 
                                                  select=True, readonly=False)
    inmoagrupacom_vpo = fields.Selection(YESNO, 'Piso VPO', 
                                                  select=True, readonly=False)
    inmoagrupacom_heating = fields.Char(compute='_get_inmoagrupacom_heating', 
                                           method=True, store=False)
    inmoagrupacom_exclusivity_doc = fields.Binary('Documento Exclusividad')
    inmoagrupacom_exclusivity_doc_url = fields.Char('Documento Exclusividad URL', size=512)
    capt_date = fields.Date('Fecha de captación')
    inmoagrupacom_capt_date = fields.Char(compute='_get_inmoagrupacom_capt_date', 
                                           method=True, store=False)
    end_date = fields.Date('Fecha fin de mandato')
    inmoagrupacom_end_date = fields.Char(compute='_get_inmoagrupacom_end_date', 
                                           method=True, store=False)
    inmoagrupacom_energy_date = fields.Char(compute='_get_inmoagrupacom_energy_date', 
                                           method=True, store=False)
    
    '''
    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(path):
            raise osv.except_osv(_('Error!'), _('The path to OpenERP medias folder does not exists on the server !'))        
        
        full_path = os.path.join(path, filename)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True
    
    def _upload_to_ftp_server(self, cr, uid, company, top, filename, context):
        directory = company.local_media_repository+top.name
        ftp = ftplib.FTP(company.ftp_host)
        if company.ftp_anonymous:
            ftp.login()
        else:
            ftp.login(company.ftp_user, company.ftp_password or '')
        if company.ftp_folder:
            try:
                ftp.mkd(company.ftp_folder+top.name)
            except Exception, e:
                print e
#             ftp.cwd(company.ftp_folder+top.name)
        ftp.quit()

#         filetype = magic.from_file(directory+'/'+filename, mime=True)
#         if filetype != 'application/pdf':
#             raise osv.except_osv(_('Error!'), 
#                          _('The certificate file should be a PDF File'))

        #ssh_cmd = 'sshpass -p "' + company.ftp_password + '" '
        ssh_cmd = 'scp ' + directory+'/'+filename + ' '
        ssh_cmd += company.ftp_user + '@' + company.ftp_host
        ssh_cmd += ':' +  company.ftp_folder + top.name
        os.system(ssh_cmd)

#         file = open(directory+'/'+filename, 'rb')
#         ftp.storbinary('STOR %s' % filename, file)
#         file.close()
        return True
    
    def _delete_file(self, cr, uid, company, top, filename, context):
        path = company.local_media_repository+top.name+'/'+filename
        if os.path.exists(path):
            os.remove(path)
        return True
    
    def _delete_from_ftp_server(self, cr, uid, company, top, 
                                filename, context):
        ftp = ftplib.FTP(company.ftp_host)
        if company.ftp_anonymous:
            ftp.login()
        else:
            ftp.login(company.ftp_user, company.ftp_password or '')
        if company.ftp_folder:
            try:
                ftp.cwd(company.ftp_folder+top.name)
            except Exception, e:
                print e
        try:
            ftp.delete(filename)
        except Exception, e:
            print e
        return True
    
    def create(self, cr, uid, vals, context=None):
        res = super(real_state_top, self).create(cr, uid, vals, context)
        if 'inmoagrupacom_exclusivity_doc' in vals:
            user = self.pool.get('res.users').browse(cr, uid, uid)
            company = user.company_id
            top = self.browse(cr,uid,res,context)
            directory = company.local_media_repository+top.name
            filename = _('exclusivity_doc_%s.pdf')%(top.name)
            if vals['inmoagrupacom_exclusivity_doc'] != False:
                self._save_file(directory, filename, vals['inmoagrupacom_exclusivity_doc'])
                if company.ftp_host:
                    self._upload_to_ftp_server(cr,uid, company, top, 
                                               filename, context)
                    energy_doc_url = company.url_media_repository+top.name+'/'+filename
                    self.write(cr,uid,res,{'inmoagrupacom_exclusivity_doc_url' : energy_doc_url},
                               context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'inmoagrupacom_exclusivity_doc' in vals:
            for top_id in ids:
                user = self.pool.get('res.users').browse(cr, uid, uid)
                company = user.company_id
                top = self.browse(cr,uid,top_id,context)
                directory = company.local_media_repository+top.name
                filename = _('exclusivity_doc_%s.pdf')%(top.name)
                if vals['inmoagrupacom_exclusivity_doc'] != False:
                    self._save_file(directory, filename, vals['inmoagrupacom_exclusivity_doc'])
                    if company.ftp_host:
                        self._upload_to_ftp_server(cr,uid, company, top, 
                                                   filename, context)
                        vals['inmoagrupacom_exclusivity_doc_url'] = company.url_media_repository+top.name+'/'+filename
                elif vals['inmoagrupacom_exclusivity_doc'] == False:
                    vals['inmoagrupacom_exclusivity_doc_url'] = False
                    self._delete_file(cr, uid, company, top, filename, context)
                    if company.ftp_host:
                        self._delete_from_ftp_server(cr, uid, company, top, 
                                                     filename, context)
                
        res = super(real_state_top, self).write(cr, uid, ids, vals, context)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        for top_id in ids:
            top = self.browse(cr,uid,top_id,context)
            directory = company.local_media_repository+top.name
            filename = _('exclusivity_doc_%s.pdf')%(top.name)
            if company.ftp_host:
                self._delete_from_ftp_server(cr, uid, company, top, 
                                             filename, context)
            self._delete_file(cr, uid, company, top, filename, context)
        
        return super(real_state_top, self).unlink(cr, uid, ids, context=context)
    '''