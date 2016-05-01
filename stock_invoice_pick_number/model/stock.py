# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Acysos S.L. <http://www.acysos.com>
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

from openerp.osv import fields, orm

class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type,
                               context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move,
                                                 partner, inv_type, context)
        
        res['name'] = '[%s - %s] %s' % (move.picking_id.origin,
                                        move.picking_id.name, move.name)
        
        return res
