# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import pymssql


class connector(models.Model):
    _name = 'connector.sqlserver'
    _rec_name = 'name'

    name = fields.Char(string='Connection name', requiered=True)
    db_name = fields.Char(string='Database Name', required=True)
    db_ip = fields.Char(string='Database IP', required=True)
    db_user = fields.Char(string='User', required=True)
    password = fields.Char(string='Pasword', required=True, password=True)
    db_port = fields.Char(string='Database port', required=True)

    def connect(self):
        server = self.db_ip + ':' + self.db_port
        try:
            conn = pymssql.connect(
                server, self.db_user, self.password, self.db_name)
        except ValueError, e:
            raise Warning(_('Connection error: ' + e))
        return conn

    def disconnect(self, conn):
        conn.close()

    @api.multi
    def getNewCursor(self, conn):
        return conn.cursor()

    @api.multi
    def selectView(self, cursor, view_name):
        cursor.execute('SELECT * FROM ' + view_name)
        return cursor
