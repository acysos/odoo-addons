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

class real_state_heating(osv.osv):
    _inherit = 'real.state.heating'
    _columns = {
        'idealistacom_type':fields.selection([
            ('0','Desconocido'),
            ('1','No disponible'),
            ('2','Independiente'),
            ('3','Central'),
            ('4','Preinstalación'),
             ],    'Tipo Idealista', select=True, readonly=False),
    }
    
    _defaults = {  
        'idealistacom_type': '0',  
        }
    
real_state_heating()

class real_state_hotwater(osv.osv):
    _inherit = 'real.state.hotwater'
    _columns = {
        'idealistacom_type':fields.selection([
            ('0','Desconocido'),
            ('1','No disponible'),
            ('2','Independiente'),
            ('3','Central'),
            ('4','Preinstalación'),
             ],    'Tipo Idealista', select=True, readonly=False),
    }
    
    _defaults = {  
        'idealistacom_type': '0',  
        }
    
real_state_hotwater()

class real_state_top(osv.osv):
    _inherit = 'real.state.top'
    
    def _get_idealistacom_operacion(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.operation=='sale' or top.operation=='sale_rent':
                value = 'sale'
            if top.operation=='rent':
                value = 'rent'
            if top.operation=='rent_sale_option':
                value = 'renttoown'
            res[top.id] = value
        return res
    
    def _get_idealistacom_precio(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.operation=='sale' or top.operation=='sale_rent':
                value = '<price>' + str(top.sale_price) + '</price>'
            if top.operation=='rent':
                value = '<price>' + str(top.rent_price) + '</price>'
            if top.operation=='rent_sale_option':
                value = '<price>' + str(top.rent_price) + '</price>\n'
                value += '<salePrice>' + str(top.sale_price) + '</salePrice>'
            res[top.id] = value
        return res
    
    def _get_idealistacom_photos(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.image_ids != False:
                for image in top.image_ids:
                    value += '<image>'
                    value += '<url>' + str(image.filename) + '</url>\n'
                    value += '<code>' + str(image.sequence) + '</code>\n'
                    value += '</image>\n'
            res[top.id] = value
        return res
    
    def _get_idealistacom_air(self, cr, uid, ids, name, arg, context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr, uid, ids, context):
            value = '0'
            if (top.office_air_conditioning != False or top.shop_air_conditioning != False):
                value = '2'
            res[top.id] = value
        return res
    
    def _get_idealistacom_heating(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
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
            #elif top.type=='industrial_unit':
            #    value = top.ground_m2
            #elif top.type=='hotel_industry':
            #    value = top.ground_m2
            #elif top.type=='parking':
            #    value = top.flat_usage_m2
            #elif top.type=='box_room':
            #    value = top.flat_usage_m2
            #elif top.type=='land':
            #    value = top.flat_usage_m2
            #elif top.type=='unlimited':
            #    value = top.flat_usage_m2
            res[top.id] = value
        return res
    
    def _get_idealistacom_hotwater(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.type=='flat':
                value = top.flat_hotwater.idealistacom_type
#             elif top.type=='shop':
#                 value = top.shop_heating.idealistacom_type
#             elif top.type=='premise':
#                 value = top.shop_heating.idealistacom_type
            elif top.type=='chalet':
                value = top.chalet_hotwater.idealistacom_type
            elif top.type=='house':
                value = top.chalet_hotwater.idealistacom_type
#             elif top.type=='office':
#                 value = top.office_heating.idealistacom_type
            #elif top.type=='industrial_unit':
            #    value = top.ground_m2
            #elif top.type=='hotel_industry':
            #    value = top.ground_m2
            #elif top.type=='parking':
            #    value = top.flat_usage_m2
            #elif top.type=='box_room':
            #    value = top.flat_usage_m2
            #elif top.type=='land':
            #    value = top.flat_usage_m2
            #elif top.type=='unlimited':
            #    value = top.flat_usage_m2
            res[top.id] = value
        return res
    
    def _get_idealistacom_orienta(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
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
            res[top.id] = value
        return res
    
    def _get_idealistacom_energyef(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
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
            res[top.id] = value
        return res
    
    def _get_idealistacom_furnished(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = '0'
            if top.furnished=='yes':
                value = '3'
            if top.furnished=='half':
                value = '3'
            if top.furnished=='no':
                value = '1'
            res[top.id] = value
        return res

    def _get_idealistacom_state(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = ''
            if top.top_state=='0':
                value = '0'
            if top.top_state=='1' or top.top_state == '3':
                value = '1'
            if top.top_state=='2':
                value = '3'
            if top.top_state=='4':
                value = '2'
            res[top.id] = value
        return res
    
    def _get_idealistacom_bathroom(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
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
            #elif top.type=='hotel_industry':
            #    value = top.ground_m2
            #elif top.type=='parking':
            #    value = top.flat_usage_m2
            #elif top.type=='box_room':
            #    value = top.flat_usage_m2
            #elif top.type=='land':
            #    value = top.flat_usage_m2
            #elif top.type=='unlimited':
            #    value = top.flat_usage_m2
            res[top.id] = value
        return res
    
    def _get_idealistacom_type(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
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
            #elif top.type=='industrial_unit':
            #    value = ''
            #elif top.type=='hotel_industry':
            #    value = ''
            elif top.type=='parking':
                value = 'garage'
            #elif top.type=='box_room':
            #    value = ''
            elif top.type=='land':
                value = 'land'
            #elif top.type=='unlimited':
            #    value = ''
            res[top.id] = value
        return res
    
    def _get_idealistacom_outside(self,cr,uid,ids,name,arg,context={}):
        if not context:
            context={}
        res = {}
        for top in self.browse(cr,uid,ids,context):
            value = '2'
            if top.outside or top.office_outside:
                value = '1'
            res[top.id] = value
        return res
    
    def onchange_idealista(self, cr, uid, ids):
        idealista_tops = self.search(cr, uid, [('idealista','=',True),
                                              ('available','=',True)])
        
        user = self.pool.get('res.users').browse(cr, uid, uid)
        
        if len(idealista_tops) >= user.company_id.idealista:
            raise osv.except_osv(_('Limite excedido!'),
                     _('Ha superado el limite de Idealista'))
        
        return True
    
    _columns = {
        'idealista': fields.boolean('Publish in idealista.com'),
        'idealistacom_operacion': fields.function(_get_idealistacom_operacion, 
                                           method=True, store=False,
                                           type='char'),
        'idealistacom_type': fields.function(_get_idealistacom_type, 
                                           method=True, store=False,
                                           type='char'),
        'idealistacom_precio': fields.function(_get_idealistacom_precio,
                                           method=True, store=False,
                                           type='char'),
        'idealistacom_photos': fields.function(_get_idealistacom_photos,
                                               method=True, store=False,
                                               type='char'),
        'idealistacom_air': fields.function(_get_idealistacom_air, method=True, 
                                           store=False, type='char'),
        'idealistacom_heating': fields.function(_get_idealistacom_heating,
                                                method=True, store=False,
                                                type='char'),
        'idealistacom_hotwater': fields.function(_get_idealistacom_hotwater,
                                                 method=True, store=False,
                                                 type='char'),
        'idealistacom_orienta': fields.function(_get_idealistacom_orienta,
                                                    method=True, store=False,
                                                    type='char'),
        'idealistacom_energyef': fields.function(_get_idealistacom_energyef,
                                                    method=True, store=False,
                                                    type='char'),
        'idealistacom_furnished': fields.function(_get_idealistacom_furnished,
                                                    method=True, store=False,
                                                    type='char'),
        'idealistacom_state': fields.function(_get_idealistacom_state,
                                                    method=True, store=False,
                                                    type='char'),
        'idealistacom_bathroom': fields.function(_get_idealistacom_bathroom,
                                                    method=True, store=False,
                                                    type='char'),
        'idealistacom_outside': fields.function(_get_idealistacom_outside,
                                                    method=True, store=False,
                                                    type='char'),
    }
    
real_state_top()