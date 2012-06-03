# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from osv import osv, fields
import tools
import os

# Trademark
class res_partner_vehicle_trademark(osv.osv):
    _description = 'Vehicles Trademark'
    _name = 'res.partner.vehicle.trademark'
    _order = 'name'
    _columns = {
        'name': fields.char('Trademark', size=64, help='The name of the trademark.', required=True, translate=True),
    }
    
res_partner_vehicle_trademark()

# Model
class res_partner_vehicle_model(osv.osv):
    _description = 'Vehicles Model'
    _name = 'res.partner.vehicle.model'
    _order = 'name'
    _columns = {
        'name': fields.char('Model', size=64, help='The name of the model.', required=True, translate=True),
        'trademark_id': fields.many2one('res.partner.vehicle.trademark', 'Trademark', required=True),
    }
    
res_partner_vehicle_model()

# Vehicles
class res_partner_vehicle(osv.osv):
    _description = 'Partner Vehicles'
    _name = 'res.partner.vehicle'
    _order = 'id'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null', select=True, help="Keep empty for a private vehicle, not related to partner."),
        'name': fields.char('Registration Number', size=128, select=1, required=True),
        'chassis_number': fields.char('Chassis Number', size=128, select=2, required=True),
        'trademark_id': fields.many2one('res.partner.vehicle.trademark', 'Trademark', select=2, required=True),
        'model_id': fields.many2one('res.partner.vehicle.model', 'Model', domain="[('trademark_id','=',trademark_id)]", select=2, required=True),
        'manufacture_date': fields.date('Manufacture Date', select=2),
        'color': fields.char('Color', size=128, select=2),
        'motor': fields.char('Motor', size=128, select=2),
        'motor_code': fields.char('Motor Code', size=128, select=2),
    }
    
res_partner_vehicle()