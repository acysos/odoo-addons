# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
import tools
import os
import time

# Sale order
class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def Child_analytic_change (self, cr, uid, ids, workorder_id, default_name, context={}):
        if default_name:
            sql = "SELECT workorder.analytic_id FROM workorder WHERE name = '%s'" % (default_name)
            cr.execute(sql)
            analytic_exist_id = cr.fetchone()[0]
            if analytic_exist_id:
                return {'value': {'project_id': analytic_exist_id}}
    
sale_order()