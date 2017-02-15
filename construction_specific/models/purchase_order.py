from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import osv, fields


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    _columns = {
        'partner_ref': fields.char('Supplier Reference', states={'confirmed':[('readonly',False)],
                                                                 'approved':[('readonly',False)],
                                                                 'done':[('readonly',False)]},
                                   copy=False,
                                   help="Reference of the sales order or bid sent by your supplier. "
                                        "It's mainly used to do the matching when you receive the "
                                        "products as this reference is usually written on the "
                                        "delivery order sent by your supplier."),
    }

    _defaults = {
        'date_order': (datetime.today() - relativedelta(days=1)).strftime(
            '%Y-%m-%d'),
    }
