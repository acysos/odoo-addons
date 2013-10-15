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

from osv import osv, fields
from tools.translate import _
import netsvc
import vatnumber

class res_partner(osv.osv):
    _inherit = "res.partner"
        
    def check_vat_vies(self, cr, uid, ids, context):
        if context is None:
            context = {}
        print "Vat vies"
        vat = False
        vat_ok = False
        european_countries = ['at','be','bg','cy','cz','de','dk','ee','el','es','fi','fr','gb','hu','ie','it','lt','lu','lv','mt','nl','pl','pt','ro','se','si','sk']
        fiscal_position = None
        
        partner_obj = self.pool.get('res.partner')
        values = {}
        partners = partner_obj.browse(cr,uid,ids,context)
        for partner in partners:
            fiscal_position = partner.property_account_position.id or None
            if partner.mag_vat:
                company = partner.company_id
                vat = partner.mag_vat
                country_code = partner.country.code
                if country_code.lower() == company.partner_id.country.code.lower():
                    if vat[:2].lower() != country_code.lower():
                        vat = country_code.upper()+vat
                    fiscal_position = company.national_fiscal_position.id or None
                else:
                    if country_code == 'GR': 
                        country_code = 'EL' #Fix Greece tax code
                    if country_code.lower() in european_countries:
                        if vat[:2].lower() != country_code.lower():
                            vat = country_code.upper()+vat
                        if vatnumber.check_vies(vat):
                            fiscal_position = company.valid_vies_fiscal_position.id or None
                        else:
                            fiscal_position = company.non_valid_vies_fiscal_position.id or None
                    else:
                        fiscal_position = company.non_european_fiscal_position.id or None
                print partner.vat
                values = {'property_account_position':fiscal_position}
                print values
                self.write(cr,uid,[partner.id],values,context)
                print "Hecho"

        return True
        
res_partner()