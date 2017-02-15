import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

class hr_timesheet_sheet(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet"
    
    def _default_date_from(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r=='month':
            return time.strftime('%Y-%m-01')
        elif r=='week':
            return (datetime.today() + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r=='year':
            return time.strftime('%Y-01-01')
        return (datetime.today() - relativedelta(days=1)).strftime('%Y-%m-%d')

    def _default_date_to(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r=='month':
            return (datetime.today() + relativedelta(months=+1,day=1,days=-1)).strftime('%Y-%m-%d')
        elif r=='week':
            return (datetime.today() + relativedelta(weekday=6)).strftime('%Y-%m-%d')
        elif r=='year':
            return time.strftime('%Y-12-31')
        return (datetime.today() - relativedelta(days=1)).strftime('%Y-%m-%d')

    _defaults = {
        'date_from': _default_date_from,
        'date_to': _default_date_to,
        'employee_id': False,
    }

class hr_timesheet_line(osv.osv):
    _inherit = "hr.analytic.timesheet"

    def _default_date(self, cr, uid, context=None):
        print context
        if 'timesheet_date_from' in context:
            return context['timesheet_date_from']
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r=='month':
            return time.strftime('%Y-%m-01')
        elif r=='week':
            return (datetime.today() + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r=='year':
            return time.strftime('%Y-01-01')
        return (datetime.today() - relativedelta(days=1)).strftime('%Y-%m-%d')

    _defaults = {
        'date': _default_date,
        }
