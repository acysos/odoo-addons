# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import time
import base64
import xlrd
import os


class PayrollImportXls(models.Model):
    _name = 'payroll.import.xls'

    date = fields.Date(string='Date account moves', readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=fields.Date.today())
    xls = fields.Binary(string='XLS', readonly=True,
                        states={'draft': [('readonly', False)]})
    note = fields.Text(string='Notes', states={'draft': [('readonly', False)]})
    software = fields.Selection(
        selection=[('none', 'None')], string='External software',
        default='none', states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[
        ('draft', 'Draft'), ('imported', 'Imported'),
        ], string='State', select=True, readonly=True, default='draft')

    @api.multi
    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(path):
            raise Warning(_('Error!'), _(
                'The path to OpenERP medias folder does '
                'not exists on the server !'))
        full_path = os.path.join(path, filename)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True

    @api.multi
    def _delete_file(self, directory, filename):
        path = directory+'/'+filename
        if os.path.exists(path):
            os.remove(path)
        return True

    @api.multi
    def import_xls(self):
        self.sudo().do_import()

    @api.multi
    def do_import(self):
        user = self.env.user
        company = user.company_id
        journal = company.payroll_journal
        directory = company.temp_file_path
        sheet_name = company.sheet_name
        filename = 'import_temp.xls'
        for import_xls in self:
            if import_xls.software != 'none':
                import_xls._save_file(directory, filename, import_xls.xls)
                workbook = xlrd.open_workbook(
                    directory+'/'+filename)
                worksheet = workbook.sheet_by_name(sheet_name)
                num_rows = worksheet.nrows - 1
                curr_row = 0
                note = _('Import moves: \n')
                period = self.env['account.period'].find(import_xls.date).id
                while curr_row < num_rows:
                    curr_row += 1
                    note, move = getattr(
                        import_xls,'_do_import_%s' % import_xls.software)(
                            note, period, journal, company, worksheet, curr_row)
                    if move and company.move_confirm:
                        try:
                            move.button_validate()
                        except Exception as fault:
                            note += '\n Move not confirmed: ' + str(fault)
                import_xls.write({'state': 'imported', 'note': note})
            else:
                raise Warning(_('Error!'), _('No software selected!'))
        return True
