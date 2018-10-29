# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import Warning
import base64
import xlrd


class PayrollImportXls(models.Model):
    _inherit = 'payroll.import.xls'
    
    software = fields.Selection(selection_add=[('csi', 'CSI')])
    
    def _do_import_csi(
            self, note, journal, company, worksheet, curr_row):
        self.ensure_one()
        moves = {}
        acc_move_obj = self.env['account.move']
        acc_move_line_obj = self.env['account.move.line']
        employee_obj = self.env['hr.employee']
        number_col = 1
        name_col = 2
        col_640 = 3
        col_476 = 4
        col_irpf = 5
        col_total = 6
        note += str(worksheet.cell_value(curr_row, name_col)) + ' \n'
        move_vals = {
            'name': worksheet.cell_value(curr_row, name_col),
            'journal_id': journal.id,
            'ref': _('Payroll'),
            'date': self.date
        }
        payroll_extid = str(int(worksheet.cell_value(curr_row, number_col)))
        employee = employee_obj.search([
            ('payroll_extid', '=', payroll_extid)])
        if not employee:
            raise Warning(
                _('Employee not found name %s') % (
                    str(worksheet.cell_value(curr_row, name_col)))
            )
        credit64 = worksheet.cell_value(curr_row, col_640)
        line64_vals = {
            'account_id': company.account_expense.id,
            'name': _('Payroll'),
            'journal_id': journal.id,
            'credit': 0,
            'debit': credit64,
            'ref': _('Payroll'),
            'tax_ids': [(6, 0, company.tax_code_base.ids)]
        }
        context = self._context.copy()
        context['journal_id'] = journal.id
        debitIRPF = worksheet.cell_value(curr_row, col_irpf)
        irpf_vals = {
            'account_id': company.account_irpf.id,
             'name': _('Payroll'),
             'journal_id': journal.id,
             'debit': 0,
             'credit': debitIRPF,
             'ref': _('Payroll'),
             'tax_line_id': company.tax_code_amount.id
        }
        debit_total = worksheet.cell_value(curr_row, col_total)
        if not employee.payroll_account:
            raise Warning(
                _('The employee %s has not payroll account') % (
                    employee.payroll_account)
            )
        total_vals = {
            'account_id': employee.payroll_account.id,
            'name': _('Payroll'),
            'journal_id': journal.id,
            'debit': 0,
            'credit': debit_total,
            'ref': _('Payroll')
            }
        debit_ss = worksheet.cell_value(curr_row, col_476)
        ss_vals = {'account_id': company.account_ss.id,
                   'name': _('Payroll'),
                   'journal_id': journal.id,
                   'debit': 0,
                   'credit': debit_ss,
                   'ref': _('Payroll')
                   }
        move_vals['line_ids'] = [
            (0, 0, line64_vals), (0, 0, irpf_vals), (0, 0, total_vals),
            (0, 0, ss_vals)]
        try:
            new_move = acc_move_obj.create(move_vals)
        except Exception as fault:
            raise Warning(
                fault.name + ' ' + move_vals['name']
            )
        return note, new_move
