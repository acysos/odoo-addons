# -*- coding: utf-8 -*-
# Copyright 2020 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import time
import logging

_logger = logging.getLogger(__name__)


class EdicomAlbaran(models.Model):
    _name = "edicom.albaran"
    _description = "Albaran Edicom"

    picking_id = fields.Many2one(
        comodel_name='stock.picking', string='Albaran', required=True)
    cabalb_ids = fields.One2many(
        comodel_name='edicom.cabalb', inverse_name='albaran_edicom_id',
        string='Datos de CABALB')
    linalb_ids = fields.One2many(
        comodel_name='edicom.linalb', inverse_name='albaran_edicom_id',
        string='Datos de LINALB')
    embalb_ids = fields.One2many(
        comodel_name='edicom.embalb', inverse_name='albaran_edicom_id',
        string='Datos de EMBALB')

    _rec_name = 'picking_id'

    @api.multi
    def procesar_albaran(self):
        cabalb_pool = self.env['edicom.cabalb']
        linalb_pool = self.env['edicom.linalb']
        embalb_pool = self.env['edicom.embalb']

        for albaran_edi in self:
            _logger.info('Albaran EDI ' + str(albaran_edi.picking_id.name))
            albaran = albaran_edi.picking_id
            if not albaran:
                raise UserError(
                    _('No se ha indicado la albaran para generar el fichero.'))

            if not (albaran.company_id and albaran.company_id.partner_id and
                    albaran.company_id.partner_id.codigo_edi):
                raise UserError(
                    _('No se ha indicado el codigo edi en la compañía del '
                      'albaran.'))

            if not (albaran.partner_id and albaran.partner_id.codigo_edi):
                raise UserError(
                    _('No se ha indicado el codigo edi en el cliente.'))

            # GENERO LA CABECERA - primero la borro si existe
            cabalb_ids = cabalb_pool.search(
                [('albaran_edicom_id', '=', albaran_edi.id)])
            cabalb_ids.unlink()
            cabalb_ids = cabalb_pool.generar(albaran_edi)

            # GENERO EMBALAJES - primero la borro si existe
            embalb_ids = embalb_pool.search(
                [('albaran_edicom_id', '=', albaran_edi.id)])
            embalb_ids.unlink()
            embalb_ids = embalb_pool.generar(albaran_edi)

            # GENERO LINEAS - primero la borro si existe
            linalb_ids = linalb_pool.search(
                [('albaran_edicom_id', '=', albaran_edi.id)])
            linalb_ids.unlink()
            linalb_ids = linalb_pool.generar(albaran_edi)

        return True


    @api.multi
    def generar_ficheros(self):
        cabalb_pool = self.env['edicom.cabalb']
        linalb_pool = self.env['edicom.linalb']
        embalb_pool = self.env['edicom.embalb']
        
        for albaran_edi in self:
            if (albaran_edi.picking_id and albaran_edi.picking_id.company_id
                    and albaran_edi.picking_id.company_id.edi_path):
                path = albaran_edi.picking_id.company_id.edi_path
            else:
                raise UserError(
                    _('No se ha indicado la ruta para generar el fichero en '
                      'la compañía de la albaran.'))
            out_char_sep = albaran_edi.picking_id.company_id.out_char_separator
            file_suffix = albaran_edi.picking_id.name.replace('/', '')

            if albaran_edi.cabalb_ids:
                cabalb_pool.exportar(
                    albaran_edi.cabalb_ids, path, file_suffix, out_char_sep)

            if albaran_edi.linalb_ids:
                linalb_pool.exportar(
                    albaran_edi.linalb_ids, path, file_suffix, out_char_sep)

            if albaran_edi.embalb_ids:
                embalb_pool.exportar(
                    albaran_edi.embalb_ids, path, file_suffix, out_char_sep)

        alert_file = open(path + '/albaranespendientes.txt', 'w')
        alert_file.close()

        return True


