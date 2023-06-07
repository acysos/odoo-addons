# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2022  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_holyday = fields.Boolean(string="Vacaciones")