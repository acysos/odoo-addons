# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
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
    "name": "Informes de cuentas anuales españoles - "
    "Entidades sin fines lucrativos",
    "version": "8.0.0.1.0",
    "author": "Acysos S.L.",
    "contributors": [
        "Ignacio Ibeas <ignacio@acysos.com>"
    ],
    "license": "AGPL-3",
    "website": "http://www.acysos.com",
    "category": "Localisation/Accounting",
    "depends": [
        'l10n_es',
        'account_balance_reporting',
    ],
    "demo": [],
    "data": [
        'data/balance_pymesfl.xml',
        'data/pyg_pymesfl.xml',
    ],
    "installable": True,
}
