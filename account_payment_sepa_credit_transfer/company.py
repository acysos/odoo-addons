##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import orm, fields
import logging

logger = logging.getLogger(__name__)


class res_company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'sepa_debtor_identifier': fields.char(
            'SEPA Credit Transfer Identifier', size=12,
            help="Enter the Identifier that has been attributed "
            "to your company to make SEPA Credit Transfers. This identifier "
            "is composed of :\n- your VAT (9 digits)\n- a "
            "3-digits subfix (commonly is 000)"),
    }

    def is_sepa_debtor_identifier_valid(
            self, cr, uid, sepa_debtor_identifier, context=None):
        """Check if SEPA Credit Transfer Identifier is valid
        @param sepa_debtor_identifier: SEPA Credit Transfer Identifier as str
            or unicode
        @return: True if valid, False otherwise
        """
        if not isinstance(sepa_debtor_identifier, (str, unicode)):
            return False
        try:
            sci_str = str(sepa_debtor_identifier)
        except:
            logger.warning(
                "SEPA Credit Transfer ID should contain only ASCII caracters.")
            return False
        sci = sci_str.lower()
        if len(sci) == 12:
            return True
        else:
            return False
        

    def _check_sepa_debtor_identifier(self, cr, uid, ids):
        for company in self.browse(cr, uid, ids):
            if company.sepa_debtor_identifier:
                if not self.is_sepa_debtor_identifier_valid(
                        cr, uid, company.sepa_debtor_identifier):
                    return False
        return True

    _constraints = [
        (_check_sepa_debtor_identifier,
            "Invalid SEPA Credit Transfer Identifier.",
            ['sepa_debtor_identifier']),
    ]
