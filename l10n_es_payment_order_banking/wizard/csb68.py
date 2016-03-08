# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 ACYSOS S.L. (http://acysos.com)
#                       Ignacio Ibeas <ignacio@acysos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _
from datetime import datetime
from log import Log


class Csb58(models.Model):
    _name = 'csb.68'
    _auto = False

    @api.model
    def _start_68(self):
        converter = self.env['payment.converter.spain']
        vat = self.order.mode.bank_id.partner_id.vat[2:]
        suffix = self.order.mode.csb_suffix
        return converter.convert(vat + suffix, 12)

    @api.model
    def _cabecera_ordenante_68(self):
        converter = self.env['payment.converter.spain']
        today = datetime.today().strftime('%d%m%y')

        text = '0359'
        text += self._start_68()
        text += 12*' '
        text += '001'
        text += today
        text += 9*' '
        # Eliminamos los espacios en blanco de la cuenta bancaria
        text += converter.convert(self.order.mode.bank_id.acc_number.replace(' ', ''), 24)
        text += 30*' '
        text += '\r\n'
        if len(text) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % ('Cabecera ordenante 68',
                                                   text), True)
        return text

    @api.model
    def _cabecera_beneficiario_68(self, recibo):
        converter = self.env['payment.converter.spain']
        text = '0659'
        text += self._start_68()
        text += converter.convert(recibo['partner_id'].vat, 12)
        return text

    @api.model
    def _registro_beneficiario_68(self, recibo):
        converter = self.env['payment.converter.spain']
        text = ''
        address = None
        partner = self.env['res.partner']
        address_ids = recibo['partner_id'].address_get(['default', 'invoice'])
        if address_ids.get('invoice'):
            address = partner.browse(address_ids.get('invoice'))
        elif address_ids.get('default'):
            address = partner.browse(address_ids.get('default'))
        else:
            raise Log(_('User error:\n\nPartner %s has no invoicing or '
                        'default address.') % recibo['partner_id'].name)

        # Primer tipo
        text1 = self._cabecera_beneficiario_68(recibo)
        text1 += '010'
        text1 += converter.convert(recibo['partner_id'].name, 40)
        text1 += 29*' '
        text1 += '\r\n'
        if len(text1) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % (
                            'Registro beneficiario tipo 1', text), True)
        text += text1

        # Segundo tipo
        text2 = self._cabecera_beneficiario_68(recibo)
        text2 += '011'
        txt_address = ''
        if address.street:
            txt_address += address.street
        if address.street2:
            txt_address += ' ' + address.street2
        text2 += converter.convert(txt_address, 45)
        text2 += 24*' '
        text2 += '\r\n'
        if len(text2) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % (
                            'Registro beneficiario tipo 2', text), True)
        text += text2

        # Tercer tipo
        text3 = self._cabecera_beneficiario_68(recibo)
        text3 += '012'
        text3 += converter.convert(address.zip, 5)
        text3 += converter.convert(address.city, 40)
        text3 += 24*' '
        text3 += '\r\n'
        if len(text3) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % (
                            'Registro beneficiario tipo 3', text), True)
        text += text3

        # Cuarto tipo
        text4 = self._cabecera_beneficiario_68(recibo)
        text4 += '013'
        text4 += converter.convert(address.zip, 9)
        text4 += converter.convert(address.state_id.name or '', 30)
        text4 += converter.convert(address.country_id.name or '', 20)
        text4 += 10*' '
        text4 += '\r\n'
        if len(text4) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % (
                            'Registro beneficiario tipo 4', text), True)
        text += text4

        # Quinto tipo
        text5 = self._cabecera_beneficiario_68(recibo)
        text5 += '014'
        text5 += 8*' ' # TODO Número de pago
        if recibo.get('ml_maturity_date'):
            date_pago = datetime.strptime(recibo['ml_maturity_date'],
                                          '%Y-%m-%d')
        elif recibo.get('date'):
            date_pago = datetime.strptime(recibo['date'], '%Y-%m-%d')
        else:
            date_pago = datetime.today()
        text5 += converter.convert(date_pago.strftime('%d%m%Y'), 8)
        text5 += converter.convert(abs(recibo['amount']), 12)
        # TODO Indicativo de presentación - Anulación
        text5 += '0'
        country_code = address.country_id and address.country_id.code or ''
        if country_code != 'ES':
            text5 += converter.convert(country_code, 2)
        else:
            text5 += 2*' '
        text5 += 6*' ' # TODO Código estadistico
        text5 += 32*' '
        text5 += '\r\n'
        if len(text5) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % (
                            'Registro beneficiario tipo 5', text), True)
        text += text5

        # Sexto tipo
        text6 = self._cabecera_beneficiario_68(recibo)
        text6 += '015'
        text6 += 8*' ' # TODO Número de pago
        text6 += converter.convert(recibo['ml_inv_ref'][0].number, 12)
        date_create = datetime.strptime(recibo['ml_date_created'], '%Y-%m-%d')
        text6 += converter.convert(date_create.strftime('%d%m%Y'), 8)
        text6 += converter.convert(abs(recibo['amount']), 12)
        text6 += 'H' # TODO Signo Negativo
        text6 += converter.convert(recibo['communication'], 26)
        text6 += 2*' '
        text6 += '\r\n'
        if len(text6) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % (
                            'Registro beneficiario tipo 6', text), True)
        text += text6

        return text

    @api.model
    def _total_general_68(self):
        converter = self.env['payment.converter.spain']
        text = '0859'
        text += self._start_68()
        text += 12*' '
        text += 3*' '
        text += converter.convert(abs(self.total_amount), 12)
        text += converter.convert(abs(self.total_payments * 6 + 2), 10)
        text += 42*' '
        text += 5*' '
        text += '\r\n'
        if len(text) % 102 != 0:
            raise Log(_('Configuration error:\n\nA line in "%s" is not 100 '
                        'characters long:\n%s') % ('Registro de totales',
                                                   text), True)
        return text

    @api.model
    def create_file(self, order, lines):
        self.order = order

        txt_file = ''
        self.total_payments = 0
        self.total_amount = 0.0

        txt_file += self._cabecera_ordenante_68()
        for recibo in lines:
            txt_file += self._registro_beneficiario_68(recibo)
            self.total_payments += 1
            self.total_amount += abs(recibo['amount'])
        txt_file += self._total_general_68()

        return txt_file
