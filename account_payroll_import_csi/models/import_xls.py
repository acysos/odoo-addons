# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models, api, _
from openerp.exceptions import Warning


class PayrollImportXls(models.Model):
    _inherit = 'payroll.import.xls'
    
    software = fields.Selection(selection_add=[('csi', 'CSI')])
    
    def _do_import_csi(
            self, note, period, journal, company, worksheet, curr_row):
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
            'period_id': period,
            'date': self.date
            }
        new_move = acc_move_obj.create(move_vals)
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
            'move_id': new_move.id,
            'journal_id': journal.id,
            'credit': 0,
            'debit': credit64,
            'ref': _('Payroll'),
            'tax_code_id': company.tax_code_base.id
            }
        context = self._context.copy()
        context['period_id'] = period
        context['journal_id'] = journal.id
        acc_move_line_obj.with_context(context).create(line64_vals)
        debitIRPF = worksheet.cell_value(curr_row, col_irpf)
        irpf_vals = {'account_id': company.account_irpf.id,
                     'name': _('Payroll'),
                     'move_id': new_move.id,
                     'journal_id': journal.id,
                     'debit': 0,
                     'credit': debitIRPF,
                     'ref': _('Payroll'),
                     'tax_code_id': company.tax_code_amount.id
                     }
        acc_move_line_obj.with_context(context).create(irpf_vals)
        debit_total = worksheet.cell_value(curr_row, col_total)
        if not employee.payroll_account:
            raise Warning(
                _('The employee %s has not payroll account') % (
                    employee.payroll_account)
            )
        total_vals = {
            'account_id': employee.payroll_account.id,
            'name': _('Payroll'),
            'move_id': new_move.id,
            'journal_id': journal.id,
            'debit': 0,
            'credit': debit_total,
            'ref': _('Payroll')
            }
        acc_move_line_obj.with_context(context).create(total_vals)
        debit_SS = worksheet.cell_value(curr_row, col_476)
        SS_vals = {'account_id': 579,
                   'name': _('Payroll'),
                   'move_id': new_move.id,
                   'journal_id': journal.id,
                   'debit': 0,
                   'credit': debit_SS,
                   'ref': _('Payroll')
                   }
        acc_move_line_obj.with_context(context).create(SS_vals)
        return note, new_move

