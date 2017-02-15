from openerp.osv import osv
import datetime


class HrHolidays(osv.osv):
    _inherit = 'hr.holidays'

    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as
         string."""

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        if timedelta.seconds > 27000:
            seconds = 27000
        else:
            seconds = timedelta.seconds
        diff_day = timedelta.days + float(seconds) / 27000
        return diff_day

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        result = super(HrHolidays, self).onchange_date_from(cr, uid, ids,
                                                            date_to, date_from)

        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = diff_day
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        result = super(HrHolidays, self).onchange_date_to(cr, uid, ids,
                                                          date_to, date_from)

        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = diff_day
        else:
            result['value']['number_of_days_temp'] = 0

        return result
