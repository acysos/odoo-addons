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

class real_state_top(osv.osv):
    _inherit = 'real.state.top'
    
    def _get_pisoscom_operacion(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            if top.operation=='sale' or top.operation=='sale_rent':
                value = 4
            if top.operation=='rent' or top.operation=='rent_sale_option':
                value = 3
            if top.operation=='transfer':
                value = 5
            res[top.id] = value
        return res
    
    def _get_pisoscom_precio(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            if top.operation=='sale' or top.operation=='sale_rent':
                value = top.sale_price
            if top.operation=='rent' or top.operation=='rent_sale_option':
                value = top.rent_price
            if top.operation=='transfer':
                value = top.sale_price
            res[top.id] = int(value)
        return res
    
    def _get_pisoscom_photos(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.image_ids != False:
                for image in top.image_ids:
                    value += '            <Foto'+str(image.sequence)+'>'
                    value += str(image.filename)
                    value += '</Foto'+str(image.sequence)+'>\n'
            res[top.id] = value
        return res
    
    def _get_pisoscom_garaje(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = '0'
            if top.parking > 0 or top.office_parking > 0:
                value = '1'
            res[top.id] = value
        return res
    
    def _get_pisoscom_heating(self, cr, uid, ids, name, arg, context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr, uid, ids, context):
            value = '0'
            if (top.flat_heating != False or top.chalet_heating != False 
                or top.office_heating != False or top.shop_heating != False):
                value = '1'
            res[top.id] = value
        return res
    
    def _get_pisoscom_air(self, cr, uid, ids, name, arg, context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr, uid, ids, context):
            value = '0'
            if (top.office_air_conditioning != False or top.shop_air_conditioning != False):
                value = '1'
            res[top.id] = value
        return res
    
    def _get_pisoscom_furnished(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = '0'
            if top.furnished == 'no':
                value = '0'
            else:
                value = '1'
            res[top.id] = value
        return res
    
    def onchange_pisoscom(self, cr, uid, ids):
        pisoscom_tops = self.search(cr, uid, [('pisoscom','=',True),
                                              ('available','=',True)])
        
        user = self.pool.get('res.users').browse(cr, uid, uid)
        
        if len(pisoscom_tops) >= user.company_id.pisoscom:
            raise osv.except_osv(_('Limite excedido!'),
                     _('Ha superado el limite de Pisos.com'))
        
        return True

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
    
    _columns = {
        'pisoscom': fields.boolean('Publish in pisos.com'),
        'pisoscom_type':fields.selection(TYPE, 'Tipo en pisos.com', 
                                              select=True, readonly=False),
        'pisoscom_operacion': fields.function(_get_pisoscom_operacion, 
                                           method=True, store=False,
                                           type='char'),
        'pisoscom_precio': fields.function(_get_pisoscom_precio, method=True, 
                                           store=False, type='char'),
        'pisoscom_number_doblehab': fields.integer('Nº Habitaciones dobles'),
        'pisoscom_number_indhab': fields.integer('Nº Habitaciones simples'),
        'pisoscom_number_banocomp': fields.integer('Nº Baños completos'),
        'pisoscom_number_banoaux': fields.integer('Nº Baños simples'),
        'pisoscom_photos': fields.function(_get_pisoscom_photos, method=True, 
                                           store=False, type='char'),
        'pisoscom_garaje': fields.function(_get_pisoscom_garaje, method=True, 
                                           store=False, type='char'),
        'pisoscom_heating': fields.function(_get_pisoscom_heating, method=True, 
                                           store=False, type='char'),
        'pisoscom_air': fields.function(_get_pisoscom_air, method=True, 
                                           store=False, type='char'),
        'pisoscom_furnished': fields.function(_get_pisoscom_furnished, 
                                              method=True, store=False, 
                                              type='char'),
    }
    
real_state_top()