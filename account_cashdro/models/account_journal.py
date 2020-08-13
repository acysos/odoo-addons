# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields
import requests
import json
import time
import webbrowser


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    cashdro_payment_terminal = fields.Boolean(
        string='Use Cashdro?')
    cashdro_ip = fields.Char(string='Cashdro IP Address',  size=45)
    cashdro_user = fields.Char(string='Cashdro User')
    cashdro_password = fields.Char(string='Cashdro Password')

    def _cashdro_operation(
            self, operationid, name, cashdro_ip, cashdro_user,
            cashdro_password, amount=0.0):
        url_send = 'https://' + cashdro_ip;
        url_send += '/Cashdro3WS/index.php?operation=startOperation';
        url_send += '&name=' + cashdro_user;
        url_send += '&password=' + cashdro_password;
        url_send += '&type=' + operationid;
        url_send += '&posid=' + name;
        url_send += '&posuser=' + str(self.env.user.id);
        if operationid in ['3', '4']:
            data = {"amount": int(round(amount, 2) * 100)}
            url_send += '&parameters=' + json.dumps(data)
        response_send = requests.get(url_send, verify=False).json()

        url_start = 'https://' + cashdro_ip
        url_start += '/Cashdro3WS/index.php?operation=acknowledgeOperationId'
        url_start += '&name=' + cashdro_user
        url_start += '&password=' + cashdro_password
        url_start += '&operationId=' + response_send['data']
        response_start = requests.get(url_start, verify=False).json()
        url_screen = 'https://' + cashdro_ip
        if operationid == '2':
            url_screen += '/Cashdro3Web/#/unload/' + response_send['data']
            url_screen += '/true/'
            url_screen += '?username=' + cashdro_user
            url_screen += '&password=' + cashdro_password
        else:
            url_screen += '/Cashdro3Web/index.html#/splash/true'
        webbrowser.open(url_screen, new=2)
        
        url_ask = 'https://' + cashdro_ip
        url_ask += '/Cashdro3WS/index.php?operation=askOperation'
        url_ask += '&name=' + cashdro_user
        url_ask += '&password=' + cashdro_password
        url_ask += '&operationId=' + response_send['data']
        response_ask = requests.get(url_ask, verify=False).json()

        response_ask_data = json.loads(response_ask['data'])
        while response_ask_data['operation']['state'] != 'F':
            time.sleep(5)
            response_ask = requests.get(url_ask, verify=False).json()
            response_ask_data = json.loads(response_ask['data'])
        
        return response_ask_data['operation']
