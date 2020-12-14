# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import time
import logging

_logger = logging.getLogger(__name__)


class EdicomFactura(models.Model):
    _name = "edicom.factura"
    _description = "Factura Edicom"

    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string='Factura', required=True)
    cabfac_ids = fields.One2many(
        comodel_name='edicom.cabfac', inverse_name='factura_edicom_id',
        string='Datos de CABFAC')
    linfac_ids = fields.One2many(
        comodel_name='edicom.linfac', inverse_name='factura_edicom_id',
        string='Datos de LINFAC')
    obsfac_ids = fields.One2many(
        comodel_name='edicom.obsfac', inverse_name='factura_edicom_id',
        string='Datos de OBSFAC')
    obslfac_ids = fields.One2many(
        comodel_name='edicom.obslfac', inverse_name='factura_edicom_id',
        string='Datos de OBSLFAC')

    _rec_name = 'invoice_id'

    @api.multi
    def procesar_factura(self):
        cabfac_pool = self.env['edicom.cabfac']
        linfac_pool = self.env['edicom.linfac']
        obsfac_pool = self.env['edicom.obsfac']
        obslfac_pool = self.env['edicom.obslfac']
        seq_pool = self.env['ir.sequence']
        journal_pool = self.env['account.journal']

        for factura_edi in self:
            _logger.info('Factura EDI ' + str(factura_edi.invoice_id.number))
            cabfac = ''
            factura = factura_edi.invoice_id

            if not factura:
                raise UserError(
                    _('No se ha indicado la factura para generar el fichero.'))

            if not (factura.company_id and factura.company_id.partner_id and
                    factura.company_id.partner_id.codigo_edi):
                raise UserError(
                    _('No se ha indicado el codigo edi en la compañía de la '
                      'factura.'))

            if not (factura.partner_id and factura.partner_id.codigo_edi):
                raise UserError(
                    _('No se ha indicado el codigo edi en el cliente.'))

            # GENERO LA CABECERA - primero la borro si existe
            cabfac_ids = cabfac_pool.search(
                [('factura_edicom_id', '=', factura_edi.id)])
            cabfac_ids.unlink()
            cabfac_ids = cabfac_pool.generar(factura_edi)

            # GENERO LINEAS - primero la borro si existe
            linfac_ids = linfac_pool.search(
                [('factura_edicom_id', '=', factura_edi.id)])
            linfac_ids.unlink()
            linfac_ids = linfac_pool.generar(factura_edi)

            # GENERO OBSERVACIONES - primero la borro si existe
            obsfac_ids = obsfac_pool.search(
                [('factura_edicom_id', '=', factura_edi.id)])
            obsfac_ids.unlink()
            obsfac_ids = obsfac_pool.generar(factura_edi)

            # GENERO OBSERVACIONES DE LINEAS - primero la borro si existe
            obslfac_ids = obslfac_pool.search(
                [('factura_edicom_id', '=', factura_edi.id)])
            obslfac_ids.unlink()
            obslfac_ids = obslfac_pool.generar(factura_edi)

        return True

    @api.multi
    def generar_ficheros(self):
        cabfac_pool = self.env['edicom.cabfac']
        linfac_pool = self.env['edicom.linfac']
        obsfac_pool = self.env['edicom.obsfac']
        obslfac_pool = self.env['edicom.obslfac']

        for factura_edi in self:
            if (factura_edi.invoice_id and factura_edi.invoice_id.company_id
                    and factura_edi.invoice_id.company_id.edi_path):
                path = factura_edi.invoice_id.company_id.edi_path
            else:
                raise UserError(
                    _('No se ha indicado la ruta para generar el fichero en '
                      'la compañía de la factura.'))
            out_char_sep = factura_edi.invoice_id.company_id.out_char_separator
            file_suffix = factura_edi.invoice_id.number.replace('/', '')

            if factura_edi.cabfac_ids:
                cabfac_pool.exportar(
                    factura_edi.cabfac_ids, path, file_suffix, out_char_sep)

            if factura_edi.linfac_ids:
                linfac_pool.exportar(
                    factura_edi.linfac_ids, path, file_suffix, out_char_sep)

            if factura_edi.obsfac_ids:
                obsfac_pool.exportar(
                    factura_edi.obsfac_ids, path, file_suffix, out_char_sep)

            if factura_edi.obslfac_ids:
                obslfac_pool.exportar(
                    factura_edi.obslfac_ids, path, file_suffix, out_char_sep)

        alert_file = open(path + '/facturaspendientes.txt', 'w')
        alert_file.close()

        return True
