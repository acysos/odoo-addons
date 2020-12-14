# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    edi_exported = fields.Boolean(string='EDI Exported', default=False)

    @api.multi
    def rexport_edicom(self):
        return self.export_edicom()

    @api.multi
    def export_edicom(self):
        edicom_factura_obj = self.env['edicom.factura']
        _logger.info('Facturas EDI')
        for invoice in self:
            _logger.info('Factura ' + str(invoice.id))
            edicom_factura = edicom_factura_obj.create(
                {'invoice_id': invoice.id})
            if (edicom_factura.procesar_factura() and
                    edicom_factura.generar_ficheros()):
                _logger.info('Facturas EDI End')
                invoice.edi_exported = True
                _logger.info('Facturas EDI Ids')
#             warning = {
#                         'title': 'Factura exportada !',
#                         'message': 'La factura se ha exportado correctamente a la pasarela de conexión con el sistema EDI.' 
#                     }
#             return {'warning': warning}
#         else:
#             warning = {
#                         'title': 'Error exportando factura !',
#                         'message': 'No ha sido posible exportar esta factura al EDI.' 
#                     }
#             return {'warning': warning}
        return True


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _line_number(self):
        for line in self:
            lines = line.invoice_id.invoice_line_ids
            line.line_number = sorted(lines).index(line)+1

    line_number = fields.Integer(
        string='Number', compute='_line_number', store=False)
