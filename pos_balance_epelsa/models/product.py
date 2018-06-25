# -*- coding: utf-8 -*-
# Copyright 2014 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import exceptions, models, fields, api, _
from odoo.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
import time
import socket
from unidecode import unidecode

_logger = logging.getLogger(__name__)


class product_balance_code(models.Model):
    _inherit = 'product.balance.code'

    @api.multi
    @api.onchange('key')
    def _onchange_key(self):
        for balance in self:
            if balance.key:
                if not len(balance.key) == 2:
                    raise ValidationError(_('The key must have 2 digits'))
                if not balance.key.isdigit():
                    raise ValidationError(_('Key between 0-9'))

    def get_checksum(self, micade):
        check = 0
        longitud_cade = len(micade)
        i = 0
        buffercheck = []
        while i < longitud_cade:
            buffercheck.append(micade[i:i + 1])
            if buffercheck[i] == chr(126):
                buffercheck[i] = chr(0)
            check = check ^ ord(buffercheck[i])
            i += 1

        check = check ^ (longitud_cade + 2)
        check = ((check & 63) | 64)

        return check

    def recv_timeout(self, the_socket, timeout=2):
        # make socket non blocking
        the_socket.setblocking(0)

        # total data partwise in an array
        total_data = []
        data = ''

        # beginning time
        begin = time.time()
        while 1:
            # if you got some data, then break after timeout
            if total_data and time.time() - begin > timeout:
                break

            # if you got no data at all, wait a little longer,
            # twice the timeout
            elif time.time() - begin > timeout * 2:
                break

            # recv something
            try:
                data = the_socket.recv(8192)
                for ch in data:
                    _logger.debug(ord(ch)),
                    _logger.debug("\n\n")
                if data:
                    total_data.append(data)
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        # join all parts to make final string
        return ''.join(total_data)

    def add_balance_epelsa_socket(self, code, balance):
        # Product
        # create an INET, STREAMing socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error:
            _logger.debug('Failed to create socket')
            return False

        _logger.debug('Socket Created')

        host = balance.ip
        port = balance.port

        try:
            remote_ip = socket.gethostbyname(host)

        except socket.gaierror:
            # could not resolve
            raise exceptions.except_orm(
                _('Error !'),
                _('Hostname could not be resolved. Exiting'))
            return False

        # Connect to remote server
        try:
            s.connect((remote_ip, port))
        except:
            raise exceptions.except_orm(
                _('Error !'), _('No route to host'))
            return False

        _logger.debug('Socket Connected to ' + host + ' on ip ' + remote_ip)

        # Send some data to remote server
        operation = '7'
        suboperation = '0'
        prod_code = '0' + code.product_id.balance_name
        price = '%07d' % (code.product_id.list_price * 100)

        if code.product_id.not_weighed:
            sale_type = 'U'
        else:
            sale_type = 'W'

        name = unidecode(code.product_id.name.ljust(25))
        message = chr(2) + operation + suboperation + prod_code + chr(0)
        message += "01" + chr(0) + code.product_id.balance_name[1:] + chr(0) +\
            "000" + chr(0)
        message += "0000" + chr(0) + price + chr(0) + sale_type + chr(0)
        message += "000" + chr(0) + "0" + chr(0) + name + chr(0)
        message += "00000" + chr(0) + chr(3)

        _logger.debug("Message: " + message)
        checksum = self.get_checksum(message)
        _logger.debug(
            "Checksum: chr(" + str(checksum) + ") = " + chr(checksum))
        message += chr(checksum) + chr(13)

        try:
            # Set the whole string
            s.sendall(message)
        except socket.error:
            # Send failed
            _logger.debug('Send failed')
            raise exceptions.except_orm(
                _('Error !'), _('Send failed %s') % name)
            return False

        _logger.debug('Message send successfully ' + message)

        # get reply and print
        _logger.debug('Reply: ' + self.recv_timeout(s))

        # Close the socket
        s.close()

        # Key
        # create an INET, STREAMing socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error:
            raise exceptions.except_orm(
                _('Error !'), _('Failed to create socket %s') % name)
            return False

        _logger.debug('Socket Created')

        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            # could not resolve
            raise exceptions.except_orm(
                _('Error !'),
                _('Hostname could not be resolved. Exiting %s') % name)
            return False

        # Connect to remote server
        s.connect((remote_ip, port))

        _logger.debug('Socket Connected to ' + host + ' on ip ' + remote_ip)

        # Send some data to remote server
        operation = '5'
        suboperation = '7'
        mode = '1'
        bal_code = balance.name
        table = '00'
        type_key = '1'
        prod_code = '0' + code.product_id.balance_name
        key = code.key
        message = chr(2) + operation + suboperation + mode + chr(0)
        message += bal_code + chr(0) + table + chr(0) + type_key + chr(0)
        message += "01" + chr(0) + key + chr(0) + prod_code + chr(3)

        _logger.debug("Message: " + message)
        checksum = self.get_checksum(message)
        _logger.debug(
            "Checksum: chr(" + str(checksum) + ") = " + chr(checksum))

        message += chr(checksum) + chr(13)

        try:
            # Set the whole string
            s.sendall(message)
        except socket.error:
            # Send failed
            raise exceptions.except_orm(
                _('Error !'), _('Send failed %s') % name)
            return False

        _logger.debug('Message send successfully ' + message)

        # get reply and print
        _logger.debug('Reply: ' + self.recv_timeout(s))

        # Close the socket
        s.close()

        # VAT
        # create an INET, STREAMing socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error:
            raise exceptions.except_orm(
                _('Error !'), _('Failed to create socket %s') % name)
            return False

        _logger.debug('Socket Created')

        try:
            remote_ip = socket.gethostbyname(host)

        except socket.gaierror:
            # could not resolve
            raise exceptions.except_orm(
                _('Error !'),
                _('Hostname could not be resolved. Exiting %s') % name)
            return False

        # Connect to remote server
        s.connect((remote_ip, port))

        _logger.debug('Socket Connected to ' + host + ' on ip ' + remote_ip)

        # Send some data to remote server
        operation = '7'
        suboperation = 'C'
        mode = '1'
        prod_code = '0' + code.product_id.balance_name
        vat = '0'
        message = chr(2) + operation + suboperation + mode + chr(0)
        message += prod_code + chr(0) + vat + chr(3)

        _logger.debug("Message:" + message)
        checksum = self.get_checksum(message)
        _logger.debug(
            "Checksum: chr(" + str(checksum) + ") = " + chr(checksum))

        message += chr(checksum) + chr(13)

        try:
            # Set the whole string
            s.sendall(message)
        except socket.error:
            # Send failed
            raise exceptions.except_orm(_('Error !'),
                                 _('Send failed %s') % name)
            return False

        _logger.debug('Message send successfully ' + message)

        # get reply and print
        _logger.debug('Reply: ' + self.recv_timeout(s))

        # Close the socket
        s.close()
        return True

    def remove_balance_epelsa_socket(self, code, balance):
        name = unidecode(code.product_id.name.ljust(25))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error:
            raise exceptions.except_orm(
                _('Error !'), _('Failed to create socket %s') % name)
            return False

        _logger.debug('Socket Created')

        host = balance.ip
        port = balance.port

        try:
            remote_ip = socket.gethostbyname(host)

        except socket.gaierror:
            # could not resolve
            raise exceptions.except_orm(
                _('Error !'),
                _('Hostname could not be resolved. Exiting %s') % name)
            return False

        # Connect to remote server
        try:
            s.connect((remote_ip, port))
        except:
            raise exceptions.except_orm(
                _('Error !'), _('No route to host'))
            return False

        _logger.debug('Socket Connected to ' + host + ' on ip ' + remote_ip)

        # Send some data to remote server
        operation = '7'
        suboperation = '2'
        mode = '1'
        prod_code = '0' + code.product_id.balance_name

        message = chr(2) + operation + suboperation + mode + chr(0)
        message += prod_code + chr(3)

        _logger.debug("Message: " + message)
        checksum = self.get_checksum(message)
        _logger.debug(
            "Checksum: chr(" + str(checksum) + ") = " + chr(checksum))

        message += chr(checksum) + chr(13)

        try:
            # Set the whole string
            s.sendall(message)
        except socket.error:
            # Send failed
            raise exceptions.except_orm(
                _('Error !'), _('Send failed {}').format(name))
            return False

        _logger.debug('Message send successfully ' + message)

        # get reply and print
        _logger.debug('Reply: ' + self.recv_timeout(s))

        # Close the socket
        s.close()
        return True

    def update_balance_epelsa_socket(self, code, balance):
        return self.add_balance_epelsa_socket(code, balance)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.onchange('balance_name')
    def _onchange_name(self):
        for product in self:
            if product.balance_name and not len(product.balance_name) == 5:
                raise ValidationError(_('The code must have 5 digits'))
            if not product.balance_name.isdigit():
                raise ValidationError(_('Code between 0-9'))

    @api.multi
    @api.onchange('key')
    def _onchange_key(self):
        for product in self:
            if not len(product.key) == 2:
                raise ValidationError(_('The key must have 2 digits'))
            if not product.key.isdigit():
                raise ValidationError(_('Key between 0-9'))
#         return self.key


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.onchange('balance_name')
    def _onchange_name(self):
        for product in self:
            if not len(product.balance_name) == 5:
                raise ValidationError(_('The code must have 5 digits'))
            if not product.balance_name.isdigit():
                raise ValidationError(_('Code between 0-9'))
