# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2013  Acysos S.L.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses.
########################################################################

from openerp.osv import fields, orm

from openerp.addons.base_iban.base_iban import _pretty_iban


_mapping = {'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15',
            'G': '16', 'H': '17', 'I': '18', 'J': '19', 'K': '20', 'L': '21',
            'M': '22', 'N': '23', 'O': '24', 'P': '25', 'Q': '26', 'R': '27',
            'S': '28', 'T': '29', 'U': '30', 'V': '31', 'W': '32', 'X': '33',
            'Y': '34', 'Z': '35'}


class WizardPartnerCcIban(orm.TransientModel):
    _name = "wizard.partner.cc.iban"
    _description = "Wizard Partner CC IBAN"

    def _bank_type_get(self, cr, uid, context=None):
        partner_bank_obj = self.pool['res.partner.bank']
        return partner_bank_obj._bank_type_get(cr, uid, context=context)

    _columns = {
        'bank_state': fields.selection(_bank_type_get, 'Bank Account Type',
                                       required=True),
    }

    def update_cc_iban(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        bank_obj = self.pool['res.partner.bank']
        partner_obj = self.pool['res.partner']
        partner_ids = context.get('active_ids')
        if partner_ids:
            for partner in partner_obj.browse(cr, uid, partner_ids,
                                              context=context):
                for bank in partner.bank_ids:
                    new_data = {}
                    country = bank.country_id
                    if not country:
                        country = partner.country_id
                        if not country:
                            country = partner.company_id.country_id
                        new_data['country_id'] = country.id
                    if bank.state == data['bank_state'] or not country:
                        continue
                    if bank.state == 'bank':
                        iban = self.convert_to_iban(
                            cr, uid, bank.acc_number, country.code,
                            context=context)
                        values = bank_obj.onchange_banco(
                            cr, uid, ids, iban, country.id, 'iban',
                            context=context)
                        if values.get('value'):
                            new_data.update(
                                {'acc_number': values['value']['acc_number'],
                                 'state': 'iban'})
                    elif bank.state == 'iban':
                        ccc = self.convert_to_ccc(
                            cr, uid, bank.acc_number, context=context)
                        values = bank_obj.onchange_banco(
                            cr, uid, ids, ccc, country.id, 'bank',
                            context=context)
                        if values.get('value'):
                            new_data.update(
                                {'acc_number': values['value']['acc_number'],
                                 'state': 'bank'})
                    if (not bank.bank or not bank.bank_bic) and \
                            'bank' in values.get('value', {}):
                        bank_data = bank_obj.onchange_bank_id(
                            cr, uid, ids, values['value']['bank'],
                            context=context)
                        new_data.update(
                            {'bank': values['value']['bank'],
                             'bank_bic': bank_data['value']['bank_bic'],
                             'bank_name': bank_data['value']['bank_name']})
                    bank_obj.write(cr, uid, [bank.id], new_data,
                                   context=context)
        return {'type': 'ir.actions.act_window_close'}

    def convert_to_iban(self, cr, uid, acc_number, country_code, context=None):
        code_char = _mapping[country_code[:1]] + _mapping[country_code[1:]]
        ccc = acc_number.replace(" ", "")
        for key, replacement in _mapping.items():
            ccc_number = ccc.replace(key, replacement)
        ccc_convert = int(ccc_number + code_char + '00')
        remainder = ccc_convert % 97
        control_digit = 98 - remainder
        if control_digit < 10:
            control_digit = '0' + str(control_digit)
        else:
            control_digit = str(control_digit)
        iban = _pretty_iban(country_code + control_digit + str(ccc))
        return iban

    def convert_to_ccc(self, cr, uid, acc_number, context=None):
        ccc = acc_number.replace(" ", "")
        acc_number = ccc[4:]
        return "%s %s %s %s" % (acc_number[0:4], acc_number[4:8],
                                acc_number[8:10], acc_number[10:])
