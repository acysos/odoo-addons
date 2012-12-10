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

from osv import fields, osv
from tools.translate import _

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'purchase_manager': fields.char('Purchase Manager', size=64,
            help="Partner Purchase Manager that confirm the sale")
    }
    
    def action_wait(self, cr, uid, ids, *args):
        sale_order = self.pool.get('sale.order').browse(cr,uid,ids)[0]
        if sale_order.partner_id.sale_order_limit > 0:
            if (sale_order.amount_untaxed > sale_order.partner_id.sale_order_limit and (sale_order.purchase_manager == False or sale_order.purchase_manager == '')):
                raise osv.except_osv(_('Confirmation !'),
                        _('This order need confirmation by the purchase manager. Write his name in the field Purchase Manager.\nSale Limit: "%i"') % \
                                (sale_order.partner_id.sale_order_limit))
        for o in self.browse(cr, uid, ids):
            if (o.order_policy == 'manual'):
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': time.strftime('%Y-%m-%d')})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': time.strftime('%Y-%m-%d')})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
            message = _("The quotation '%s' has been converted to a sales order.") % (o.name,)
            self.log(cr, uid, o.id, message)
            
        return True
        
sale_order()