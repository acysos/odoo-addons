# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import Warning
import base64
import xlrd


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
    def import_xls(self):
        self.sudo().do_import()

    @api.multi
    def do_import(self):
        user = self.env.user
        company = user.company_id
        journal = company.payroll_journal
        sheet_name = company.sheet_name
        filename = 'import_temp.xls'
        for import_xls in self:
            if import_xls.software != 'none':
                workbook = xlrd.open_workbook(
                    file_contents = base64.decodestring(import_xls.xls))
                worksheet = workbook.sheet_by_name(sheet_name)
                num_rows = worksheet.nrows - 1
                curr_row = 0
                note = _('Import journal entries: \n')
                while curr_row < num_rows:
                    curr_row += 1
                    note, move = getattr(
                        import_xls,'_do_import_%s' % import_xls.software)(
                            note, journal, company, worksheet, curr_row)
                    if move and company.move_confirm:
                        try:
                            move.button_validate()
                        except Exception as fault:
                            note += '\n Journal entry not confirmed: ' 
                            note += str(fault)
                import_xls.write({'state': 'imported', 'note': note})
            else:
                raise Warning(_('Error!'), _('No software selected!'))
        return True
