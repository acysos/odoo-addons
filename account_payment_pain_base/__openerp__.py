##############################################################################
#
#    PAIN base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#    Copyright (C) 2014 Acysos S.L. (<http://acysos.com>).
#    @author: Ignacio Ibeas <ignacio@acysos.com>
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
{
    'name': 'Account Payment PAIN Base Module',
    'summary': 'Base module for PAIN file generation',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Akretion, Noviat, Acysos',
    'website': 'http://openerp-community-association.org/',
    'category': 'Hidden',
    'depends': ['account_payment_extension','account_payment_export'],
#    'external_dependencies': {
#        'python': ['unidecode', 'lxml'],
#        },
    'data': [
        'payment_line_view.xml',
        'payment_mode_view.xml',
        'company_view.xml',
    ],
    'description': '''
Base module for PAIN file generation
====================================

This module contains fields and functions that are used by the module for SEPA Credit Transfer (account_banking_sepa_credit_transfer) and SEPA Direct Debit (account_banking_sepa_direct_debit). This module doesn't provide any functionnality by itself.

This module is part of the banking addons: https://launchpad.net/account-payment

For windows server copy the 'unidecode' folder of https://pypi.python.org/pypi/Unidecode/ to the OpenERP Server Folder.

This module was started during the Akretion-Noviat code sprint of November 21st 2013 in Epiais les Louvres (France).
Adapted to account_payment_extension by Acysos S.L. <info@acysos.com>
    ''',
    'active': False,
    'installable': True,
}
