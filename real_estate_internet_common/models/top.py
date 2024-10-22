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

class real_estate_top(models.Model):
    _inherit = 'real.estate.top'
    
    TOP_STATE = [
            ('0','Desconocido'),
            ('1','Nuevo'),
            ('2','Bien Conservado'),
            ('3','Nueva Construcción'),
            ('4','Para Reformar'),
            ('5','Reformado'),
             ]
    
    def _get_googlemap_url(self):
        for top in self:
            if top.latitude and top.longitude:
                url = 'http://maps.google.com/maps?q='
                url += top.latitude
                url += ','
                url += top.longitude
                url += '&ll='
                url += top.latitude
                url += ','
                url += top.longitude
                url += '&z=17'
                top.google_maps_url = url

    def _get_openstreetmap_url(self):
        for top in self:
            if top.latitude and top.longitude:
                url = 'http://www.openstreetmap.org/?mlat='
                url += top.latitude
                url += '&mlon='
                url += top.longitude
                url += '&zoom=17'
                top.openstreetmap_url = url

    door = fields.Char(string='Puerta')
    latitude = fields.Char('Latitud')
    longitude = fields.Char('Longitud')
    top_state = fields.Selection(TOP_STATE,
                                 'Estado de conservación', select=True)
    google_maps_url = fields.Char(
        string='Google Maps URL', compute=_get_googlemap_url,store=True)
    openstreetmap_url = fields.Char(
        string='Openstreemap URL', compute=_get_openstreetmap_url,store=True)
    