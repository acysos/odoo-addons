# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 OpenERP SA (<http://openerp.com>)
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

import logging
import string
import datetime
import re
_logger = logging.getLogger(__name__)
from openerp.osv import fields, osv
from openerp.tools.misc import ustr
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def check_vat(self, cr, uid, ids, context=None):
        return True
    
    def _construct_constraint_msg(self, cr, uid, ids, context=None):
        def default_vat_check(cn, vn):
            # by default, a VAT number is valid if:
            #  it starts with 2 letters
            #  has more than 3 characters
            return cn[0] in string.ascii_lowercase and cn[1] in string.ascii_lowercase
        vat_country, vat_number = self._split_vat(self.browse(cr, uid, ids)[0].vat)
        vat_no = "'CC##' (CC=Country Code, ##=VAT Number)"
        error_partner = self.browse(cr, uid, ids, context=context)
        if default_vat_check(vat_country, vat_number):
            vat_no = _ref_vat[vat_country] if vat_country in _ref_vat else vat_no
            if self.pool['res.users'].browse(cr, uid, uid).company_id.vat_check_vies:
                return '\n' + _('The VAT number [%s] for partner [%s] either failed the VIES VAT validation check or did not respect the expected format %s.') % (error_partner[0].vat, error_partner[0].name, vat_no)
        return '\n' + _('The VAT number [%s] for partner [%s] does not seem to be valid. \nNote: the expected format is %s') % (error_partner[0].vat, error_partner[0].name, vat_no)
    
    _constraints = [(check_vat, _construct_constraint_msg, ["vat"])]
