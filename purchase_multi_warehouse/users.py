# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#        All Rights Reserved, Jesús Martín <jmartin@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import osv, fields

class users(osv.osv):
    _inherit  =  "res.users"
    _columns  =  {
        'warehouse_ids': fields.many2many('stock.warehouse', 
                                          'warehouse_user_rel', 'warehouse_id', 
                                          'user_id', "Warehouses"),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', 
                                        help='The current warehouse related to the user'),
    }

    def __init__(self, *args):
        super(users, self).__init__(*args)
        if 'warehouse_id' not in self.SELF_WRITEABLE_FIELDS:
            self.SELF_WRITEABLE_FIELDS.append('warehouse_id')

users()
