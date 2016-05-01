# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
    
class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
            'date_planned': fields.datetime('Date planned'), 
                    }

    def _get_date_planned(self, cr, uid, order, line, start_date,
                          context=None):
        if order.date_planned:
            date_planned = order.date_planned
        else:
            date_planned = super(sale_order, self)._get_date_planned(
                cr, uid,order, line, start_date, context=None)
        return date_planned
