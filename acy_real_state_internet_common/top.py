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
    
    TOP_STATE = [
            ('0','Unknown'),
            ('1','New'),
            ('2','Well-conserved'),
            ('3','New construction'),
            ('4','To remodelate'),
            ('5','Remodelated'),
             ]

    _columns = {
        'door':fields.char('Door', size=64, required=False, readonly=False),
        'latitude':fields.char('Latitude', size=64, required=False,
                               readonly=False),
        'longitude':fields.char('Longitude', size=64, required=False,
                                readonly=False),
        'top_state':fields.selection(TOP_STATE, 
                           'State of conservation', select=True, readonly=False),
    }
    
real_state_top()