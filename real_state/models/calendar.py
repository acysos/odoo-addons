# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
#           Daniel Pascal <daniel@acysos.com>
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
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import time

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    top_id = fields.Many2one('real.state.top', 'Top', required=False)
        
    @api.onchange('top_id')
    def onchange_top_id(self):
        if self.top_id:
            name = self.top_id.name + '-' + self.top_id.address
            if self.top_id.number != False: 
                name += ' ' + self.top_id.number            
            if self.floor != False: 
                name += ' ' + self.top_id.floor           
            if self.stair != False: 
                name += ' ' + self.top_id.stair
            self.location = name
        
        
    