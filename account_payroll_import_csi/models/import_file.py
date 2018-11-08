# -*- coding: utf-8 -*-
# Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
# Copyright (c) 2018 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import Warning


class ImportFile(models.Model):
    _inherit = 'import.file'
    
    software = fields.Selection(selection_add=[('csi', 'CSI')])
    
    def _do_import_xls_csi(
            self, worksheet, curr_row):
        self.ensure_one()
        moves = {}
        acc_move_obj = self.env['account.move']
        employee_obj = self.env['hr.employee']
        company = self.company
        journal = company.payroll_journal
        number_col = 1
        name_col = 2
        col_640 = 3
        col_476 = 4
        col_irpf = 5
        col_total = 6
        self.note += str(worksheet.cell_value(curr_row, name_col)) + ' \n'
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
        if employee.address_home_id:
            partner_id = employee.address_home_id.id
        else:
            partner_id = False
            self.note += _(
                'Employee %s has not private address for AEAT 111 \n') % (
                    str(worksheet.cell_value(curr_row, name_col)))
        credit64 = worksheet.cell_value(curr_row, col_640)
        if not self.company.account_expense:
            raise Warning(_('No expense account configure in company!'))
        line64_vals = {
            'account_id': company.account_expense.id,
            'name': _('Payroll'),
            'journal_id': journal.id,
            'credit': 0,
            'debit': credit64,
            'ref': _('Payroll'),
            'tax_ids': [(6, 0, company.tax_code_base.ids)],
            'partner_id': partner_id
        }
        context = self._context.copy()
        context['journal_id'] = journal.id
        debitIRPF = worksheet.cell_value(curr_row, col_irpf)
        if not self.company.account_irpf:
            raise Warning(_('No IRPF account configure in company!'))
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
        if company.payroll_payment_mode:
            total_vals['payment_mode_id'] = company.payroll_payment_mode.id
        debit_ss = worksheet.cell_value(curr_row, col_476)
        if not self.company.account_ss:
            raise Warning(_('No SS account configure in company!'))
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
        return new_move
