# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2025  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError as Warning
import pymssql, logging

logger = logging.getLogger(__name__)


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
        for res in self:
            server = res.db_ip + ':' + res.db_port
            try:
                conn = pymssql.connect(
                    host=server, user=res.db_user,
                    password=res.password, database=res.db_name,
                    encryption='off')
                logger.info('Conexion realizada ' + res.db_name)
            except pymssql.OperationalError as e:
                print(e)
                raise Warning(_('Connection error: ' + str(e)))
        return conn

    def disconnect(self, conn):
        conn.close()

    def getNewCursor(self, conn):
        return conn.cursor()

    def selectView(self, cursor, view_name):
        cursor.execute('SELECT * FROM ' + view_name)
        return cursor
