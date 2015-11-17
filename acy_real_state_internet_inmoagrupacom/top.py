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
import base64
import os
from ftplib import FTP
import magic
import datetime

class real_state_top(osv.osv):
    _inherit = 'real.state.top'

    def _get_inmoagrupacom_gestiones(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = '<gestion>\n'
            if top.operation=='sale' or top.operation=='sale_rent':
                value += '\t\t\t<tipo><![CDATA[Venta]]></tipo>\n'
                value += '\t\t\t<precio>'+str(top.sale_price)+'</precio>\n'
            if top.operation=='rent':
                value += '\t\t\t<tipo><![CDATA[Alquiler]]></tipo>\n'
                value += '\t\t\t<precio>'+str(top.rent_price)+'</precio>\n'
            if top.operation=='rent_sale_option':
                value += '\t\t\t<tipo><![CDATA[Alquiler opción compra]]></tipo>\n'
                value += '\t\t\t<precio>'+str(top.rent_price)+'</precio>\n'
            if top.operation=='transfer':
                value += '\t\t\t<tipo><![CDATA[Traspaso]]></tipo>\n'
                value += '\t\t\t<precio>'+str(top.sale_price)+'</precio>\n'
            value += '\t\t\t<honorarios_tipo>'+str(top.inmoagrupacom_fee_type or '')+'</honorarios_tipo>\n'
            value += '\t\t\t<honorarios_agente_captador>'+str(top.inmoagrupacom_fee_captador or '')+'</honorarios_agente_captador>\n'
            value += '\t\t\t<honorarios_agente_colaborador>'+str(top.inmoagrupacom_fee_colaborador or '')+'</honorarios_agente_colaborador>\n'
            value += '\t\t\t<comision_referido>'+str(top.inmoagrupacom_commission_refer or '')+'</comision_referido>\n'
            value += '\t\t    </gestion>\n'
            res[top.id] = value
        return res
    
    def _get_inmoagrupacom_heating(self, cr, uid, ids, name, arg, context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr, uid, ids, context):
            value = ''
            if (top.flat_heating != False or top.chalet_heating != False 
                or top.office_heating != False or top.shop_heating != False):
                value = '1'
            res[top.id] = value
        return res
    
    def _get_inmoagrupacom_photos(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.image_ids != False:
                value += '<fotos>\n'
                for image in top.image_ids:
                    value += '\t\t    <foto>\n'
                    value += '\t\t\t<url_foto><![CDATA['+str(image.filename)+']]></url_foto>\n'
                    value += '\t\t\t<descripcion_foto><![CDATA['+str(image.comments or '')+']]></descripcion_foto>\n'
                    if (image.sequence == 1):
                        value += '\t\t\t<principal_01>1</principal_01>\n'
                    else:
                        value += '\t\t\t<principal_01>0</principal_01>\n'
                    value += '\t\t\t<tipo_foto>0</tipo_foto>\n'
                    value += '\t\t\t<orden_foto>'+str(image.sequence)+'</orden_foto>\n'
                    value += '\t\t    </foto>\n'
                value += '\t\t</fotos>\n'
            res[top.id] = value
        return res
    
    def _get_inmoagrupacom_capt_date(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.capt_date:
                value = datetime.datetime.strptime(top.capt_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            res[top.id] = value
        return res
    
    def _get_inmoagrupacom_end_date(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.end_date:
                value = datetime.datetime.strptime(top.end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            res[top.id] = value
        return res
    
    def _get_inmoagrupacom_energy_date(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.energy_date:
                value = datetime.datetime.strptime(top.energy_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            res[top.id] = value
        return res
    
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
            ('Otros [Pisos]','Otros [Pisos]'),
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
            ('Otros [Casas/Chalets]','Otros [Casas/Chalets]'),
            ('Cortijo','Cortijo'),
            ('Casona','Casona'),
            ('Mansión','Mansión'),
            ('Cabaña','Cabaña'),
            ('Oficina','Oficina'),
            ('Almacén','Almacén'),
            ('Nave Industrial','Nave Industrial'),
            ('Otros [Naves]','Otros [Naves]'),
            ('Bar','Bar'),
            ('Restaurante','Restaurante'),
            ('Txoko','Txoko'),
            ('Residencia','Residencia'),
            ('Granja','Granja'),
            ('Otros [Explotaciones]','Otros [Explotaciones]'),
            ('Edificio','Edificio'),
            ('Hostal-Pensión','Hostal-Pensión'),
            ('Peña Gastronómica','Peña Gastronómica'),
            ('Polígono','Polígono'),
            ('Hotel','Hotel'),
            ('Balneario','Balneario'),
            ('Otros [Terrenos]','Otros [Terrenos]'),
            ('Finca Urbanizable','Finca Urbanizable'),
            ('Solar','Solar'),
            ('Finca Rustica','Finca Rustica'),
            ('Finca','Finca'),
            ('Finca Agraria','Finca Agraria'),
            ('Otros [Locales]','Otros [Locales]'),
            ('Garaje','Garaje'),
            ('Trastero','Trastero'),
             ]
    
    YESNO = [('0', 'No'), ('1', 'Si')]

    _columns = {
        'inmoagrupacom': fields.boolean('Publish in inmoagrupa.com'),
        'inmoagrupacom_street_type':fields.selection(STREET_TYPE, 
                                 'Tipo de calle', select=True, readonly=False),
        'inmoagrupacom_type':fields.selection(TYPE, 'Tipo en inmoagrupa.com', 
                                              select=True, readonly=False),
        'inmoagrupacom_piso':fields.char('Piso', size=64, 
                                             required=False, readonly=False),
        'inmoagrupacom_letra':fields.char('Letra', size=64, 
                                             required=False, readonly=False),
        'inmoagrupacom_gestiones': fields.function(_get_inmoagrupacom_gestiones, 
                                           method=True, store=False,
                                           type='char'),
        'inmoagrupacom_latitude':fields.char('Latitud', size=64, 
                                             required=False, readonly=False),
        'inmoagrupacom_longitude':fields.char('Longitud', size=64, 
                                             required=False, readonly=False),
        'inmoagrupacom_fee_type':fields.selection(FEE_TYPE,'Tipo honarios', 
                                                  select=True, readonly=False),
        'inmoagrupacom_fee_captador': fields.float('Honorarios captador'), 
        'inmoagrupacom_fee_colaborador': fields.float('Honorarios colaborador'),
        'inmoagrupacom_commission_refer': fields.float('Comisión referido'),
        'inmoagrupacom_bank':fields.selection(YESNO, 'Piso Banco', 
                                                  select=True, readonly=False),
        'inmoagrupacom_vpo':fields.selection(YESNO, 'Piso VPO', 
                                                  select=True, readonly=False),
        'inmoagrupacom_heating': fields.function(_get_inmoagrupacom_heating, 
                                           method=True, store=False,
                                           type='char'),
        'inmoagrupacom_photos': fields.function(_get_inmoagrupacom_photos, 
                                           method=True, store=False,
                                           type='char'),
        'inmoagrupacom_exclusivity_doc': fields.binary('Documento Exclusividad'),
        'inmoagrupacom_exclusivity_doc_url': fields.char('Documento Exclusividad URL', size=512),
        'capt_date': fields.date('Fecha de captación'),
        'inmoagrupacom_capt_date': fields.function(_get_inmoagrupacom_capt_date, 
                                           method=True, store=False,
                                           type='char'),
        'end_date': fields.date('Fecha fin de mandato'),
        'inmoagrupacom_end_date': fields.function(_get_inmoagrupacom_end_date, 
                                           method=True, store=False,
                                           type='char'),
        'inmoagrupacom_energy_date': fields.function(_get_inmoagrupacom_energy_date, 
                                           method=True, store=False,
                                           type='char'),
    
    }
    
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
        ftp = FTP(company.ftp_host)
        if company.ftp_anonymous:
            ftp.login()
        else:
            ftp.login(company.ftp_user, company.ftp_password or '')
        if company.ftp_folder:
            try:
                ftp.mkd(company.ftp_folder+top.name)
            except Exception, e:
                print e
            ftp.cwd(company.ftp_folder+top.name)
        filetype = magic.from_file(directory+'/'+filename, mime=True)
        if filetype != 'application/pdf':
            raise osv.except_osv(_('Error!'), 
                         _('The certificate file should be a PDF File'))
         
        file = open(directory+'/'+filename, 'rb')
        ftp.storbinary('STOR %s' % filename, file)
        file.close()
        return True
    
    def _delete_file(self, cr, uid, company, top, filename, context):
        path = company.local_media_repository+top.name+'/'+filename
        if os.path.exists(path):
            os.remove(path)
        return True
    
    def _delete_from_ftp_server(self, cr, uid, company, top, 
                                filename, context):
        ftp = FTP(company.ftp_host)
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
    
real_state_top()