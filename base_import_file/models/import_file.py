# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import Warning
import base64
import xlrd


class ImportFile(models.Model):
    _name = 'import.file'

    name = fields.Char(
        string='Name', required=True, default=lambda self: _('New'),
        readonly=True, states={'draft': [('readonly', False)]})
    company = fields.Many2one(
        comodel_name='res.company', string='Company', readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(),
        states={'draft': [('readonly', False)]})
    date = fields.Date(
        string='Date import', readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.today())
    file = fields.Binary(
        string='File', readonly=True,
        states={'draft': [('readonly', False)]})
    file_type = fields.Selection(
        selection=[('none', 'None'), ('xls', 'Excel XLS(X)')],
        default='none', readonly=True,
        states={'draft': [('readonly', False)]})
    note = fields.Text(
        string='Notes', readonly=True, states={'draft': [('readonly', False)]})
    software = fields.Selection(
        selection=[('none', 'None')], string='External software',
        default='none', readonly=True, states={'draft': [('readonly', False)]})
    sheet_name = fields.Char(
        string='Sheet name', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[
        ('cancel', 'Cancelled'), ('draft', 'Draft'), ('imported', 'Imported'),
        ], string='State', select=True, readonly=True, default='draft')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code(
                        'import.file') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'import.file') or _('New')
        result = super(ImportFile, self).create(vals)
        return result

    @api.multi
    def import_file(self):
        for import_file in self:
            if import_file.software != 'none':
                if import_file.file_type == 'none':
                    raise Warning(_('Error!'), _('No format file selected!'))
                elif import_file.file_type == 'xls':
                    self.sudo().do_import_xls()
                else:
                    raise Warning(_('Format file not supported!'))
            else:
                raise Warning(_('No software selected!'))
                

    @api.multi
    def before_operations(self):
        self.ensure_one()

    @api.multi
    def after_operations(self, object):
        self.ensure_one()
    
    @api.multi
    def cancel_import(self):
        self.ensure_one()
        self.state = 'cancel'
        self.note = False

    @api.multi
    def change_to_draft(self):
        self.ensure_one()
        self.state = 'draft'

    @api.multi
    def do_import_xls(self):
        self.ensure_one()
        sheet_name = False
        if self.company.sheet_name:
            sheet_name = self.company.sheet_name
        if self.sheet_name:
            sheet_name = self.sheet_name
        if not sheet_name:
            raise Warning(_('No sheet name configure in company!'))
        sheet_name = self.company.sheet_name            
        self.note = _('Import file: \n')
        self.before_operations()
        workbook = xlrd.open_workbook(
            file_contents = base64.decodestring(self.file))
        worksheet = workbook.sheet_by_name(sheet_name)
        num_rows = worksheet.nrows - 1
        curr_row = 0
        while curr_row < num_rows:
            curr_row += 1
            object = getattr(
                self,'_do_import_xls_%s' % self.software)(
                    worksheet, curr_row)
            if object:
                self.after_operations(object)
        self.state = 'imported'
