# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import Warning


class ImportFile(models.Model):
    _inherit = 'import.file'

    @api.multi
    def _count_account_moves(self):
        for import_file in self:
            count = self.env['account.move'].search_count(
                [('import_file_id', '=', import_file.id)])
            import_file.count_payroll = count

    payroll = fields.Boolean(string='Is payroll')
    count_payroll = fields.Integer(
            string='Moves count', compute='_count_account_moves')

    @api.multi
    def after_operations(self, object):
        self.ensure_one()
        if not object.import_file_id:
            object.import_file_id = self.id
        if object and self.company.move_confirm:
            try:
                object.post()
            except Exception as fault:
                self.note += '\n Journal entry not confirmed: ' 
                self.note += str(fault)
        super(ImportFile, self).after_operations(object)

    @api.multi
    def cancel_import(self):
        self.ensure_one()
        super(ImportFile, self).cancel_import()
        if self.state == 'cancel':
            moves = self.env['account.move'].search(
                [('import_file_id', '=', self.id)])
            for move in moves:
                try:
                    if move.state == 'posted':
                        move.button_cancel()
                    move.unlink()
                except Exception as fault:
                    self.note += '\n Journal entry not cancelled: '
                    self.note += str(fault)
