# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import tools
import os

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _vat_truncate(self,cr,uid,ids,name,arg,context={}):
        res={}
        for partner in self.browse(cr,uid,ids,context):
            if partner.country == partner.company_id.partner_id.country:
                res[partner.id] = partner.vat[2:]
            else:
                res[partner.id] = partner.vat
        return res
    
    _columns = {
        'vat_truncate': fields.function(_vat_truncate, method=True, type='char', size=32, string='VAT Truncate', readonly=True),
    }

res_partner()