# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.http import request

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_ip = fields.Char(string="Check In IP Address",
        readonly=True)
    check_out_ip = fields.Char(string="Check Out IP Address",
        readonly=True)

    @api.constrains("check_in")
    def _set_check_in_ip(self):
        for attendance in self:
            if attendance.check_in:
                if request:
                    if request.httprequest:
                        if request.httprequest.remote_addr:
                            attendance.check_in_ip = \
                                request.httprequest.remote_addr

    @api.constrains("check_out")
    def _set_check_out_ip(self):
        for attendance in self:
            if attendance.check_out:
                if request:
                    if request.httprequest:
                        if request.httprequest.remote_addr:
                            attendance.check_out_ip = \
                                request.httprequest.remote_addr