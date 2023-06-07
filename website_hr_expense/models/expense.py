# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

class HeExpense(models.Model):
    _inherit = 'hr.expense'

    def portal_create_sheet(self):
        return self.sudo()._create_sheet_from_expenses()
