# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com> Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class hr_expense_expense(models.Model):
    _inherit = 'hr.expense.expense'

    def _default_date(self, cr, uid, context=None):
        return (datetime.today() - relativedelta(days=1)).strftime('%Y-%m-%d')

    date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)],
                'refused': [('readonly', False)]},
        default=_default_date, string="Date")
