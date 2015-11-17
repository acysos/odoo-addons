# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################
from osv import osv
from osv import fields
import decimal_precision as dp
from tools.translate import _
import time

class crm_meeting(osv.osv):
    _inherit = 'crm.meeting'

    _columns = {
            'top_id':fields.many2one('real.state.top', 'Top', required=False), 
        }
    def onchange_top_id(self, cr, uid, ids, top_id, context=None):
        if not context:
            context={}
        top_obj = self.pool.get('real.state.top')
        top = top_obj.browse(cr, uid, top_id, context)
                
        name = top.name + '-' + top.address
        if top.number != False: 
            name += ' ' + top.number            
        if top.floor != False: 
            name += ' ' + top.floor           
        if top.stair != False: 
            name += ' ' + top.stair
        
        value = {'location': name}
        
        return {'value': value}
crm_meeting()