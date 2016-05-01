# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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
from openerp import netsvc
from openerp import SUPERUSER_ID, api

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, picking_ids, context=None):
        super(stock_picking, self).do_transfer(cr, uid, picking_ids, context)
        sequence_obj = self.pool.get('ir.sequence')
        for picking in self.browse(cr, uid, picking_ids, context):
            if picking.picking_type_id.code == 'outgoing':
                sequence = sequence_obj.get(cr, uid, 'stock.picking.sent')
                self.write(cr, uid, [picking.id], {'name': sequence})
            
        return True
