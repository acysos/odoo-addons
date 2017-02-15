from openerp.osv import fields, osv
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class hr_expense_expense(osv.osv):
    _inherit = 'hr.expense.expense'

    def _default_date(self, cr, uid, context=None):
        return (datetime.today() - relativedelta(days=1)).strftime('%Y-%m-%d')

    _defaults = {
        'date': _default_date,
    }
