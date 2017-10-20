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

    door = fields.Char(string='Puerta')
    latitude = fields.Char('Latitud')
    longitude = fields.Char('Longitud')
    top_state = fields.Selection(TOP_STATE,
                                 'Estado de conservación', select=True)
    