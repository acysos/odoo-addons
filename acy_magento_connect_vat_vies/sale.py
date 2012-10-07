# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
from tools.translate import _

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    
    _columns = {
        'national_fiscal_position': fields.many2one('account.fiscal.position', 'National Fiscal Position',help='Default Fiscal position for the partners with fiscal address in the same country that the company'),
        'non_vat_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for non-Vat', help='Default Fiscal position for partners without vat number'),
        'valid_vies_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for Valid Vies Vat', help='Default Fiscal position for partners with a valid vat number in vies validation webservices'),
        'non_valid_vies_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for non-Valid Vies Vat', help='Default Fiscal position for partners without a valid vat number in vies validation webservices'),
        'non_european_fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position for non-European', help='Default Fiscal position for partners outside Europe'),
    }
sale_shop()