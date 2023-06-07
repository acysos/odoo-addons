# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2019  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ext_attendance = fields.Boolean('Fichar en portal')
    tester = fields.Boolean('tester portal')

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    ext_attendance = fields.Boolean('Fichar en portal')
    tester = fields.Boolean('tester portal')
