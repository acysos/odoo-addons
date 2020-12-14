# -*- coding: utf-8 -*-
# Copyright 2020 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from checkdigit import upc
import logging
import re
from datetime import datetime

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_edicom_total_quantity(self):
        for picking in self:
            sumqty = 0
            for line in picking.move_lines:
                sumqty += line.quantity_done
            picking.edicom_totqty = sumqty

    @api.multi
    def _get_sscc(self):
        for picking in self:
            code = picking.company_id.edi_sscc_init or '0'
            code += picking.company_id.edi_sscc_code
            quant_name = re.sub("[^0-9]", "", picking.name.split('/')[2])
            if quant_name[0:1] == '0':
                quant_name = quant_name[1:]
            quant_name = str(datetime.now().year)[-2:] + quant_name
            code += quant_name[-9:].zfill(9)
            control_digit = upc.upc_calculate(code)
            code += control_digit
            picking.sscc_code = code

    edicom_dock = fields.Many2one(
        comodel_name='res.partner', string='Muelle',
        help="Codigo EDI del muelle de entrega")
    edicom_portes = fields.Selection(
        string='Portes',
        selection=[('PP', 'Portes pagados'), ('CC', 'Ported Debidos'),
                   ('DF', 'Método definido por el comprador y proveedor'),
                   ('PC', 'Pago adelantado pero cargado al cliente')])
    edicom_recogida = fields.Selection(
        string='Recogida',
        selection=[('RD', 'Mercancía recogida por el emisor del pedido'),
                   ('EP', 'Mercancía enviada por el receptor del pedido'),
                   ('01E', 'Contactar con la parte receptora antes de la '
                    'entrega (c. EAN)'),
                   ('02E', 'Enviar mercancía, entrega urgente (código EAN)')])
    edicom_tiptrans = fields.Selection(
        string='Tipo de transporte',
        selection=[('10', 'Transporte marítimo'),
                   ('20', 'Transporte ferroviario'),
                   ('30', 'Transporte por carretera'),
                   ('40', 'Transporte aéreo'),
                   ('60', 'Transporte multimode')])
    edicom_idtrans = fields.Many2one(
        comodel_name='res.partner', string='Is Transportista',
        help="Codigo EDI del transportista")
    edicom_totqty = fields.Float(
        string='Cantidad total', compute='_get_edicom_total_quantity')
    edi_exported = fields.Boolean(string='EDI Exported', default=False)
    sscc_code = fields.Char(string="SSCC Code", compute=_get_sscc)

    @api.multi
    def rexport_edicom(self):
        return self.export_edicom()

    @api.multi
    def export_edicom(self):
        edicom_albaran_obj = self.env['edicom.albaran']
        _logger.info('Albaranes EDI')
        for picking in self:
            _logger.info('Albaran ' + str(picking.id))
            edicom_albaran = edicom_albaran_obj.create(
                {'picking_id': picking.id})
            if (edicom_albaran.procesar_albaran() and
                    edicom_albaran.generar_ficheros()):
                _logger.info('Albaranes EDI End')
                picking.edi_exported = True
                _logger.info('Albaranes EDI Ids')
        return True


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.multi
    def _get_sscc(self):
        for quant in self:
            code = quant.company_id.edi_sscc_init or '3'
            code += quant.company_id.edi_sscc_code or '8435173'
            quant_name = re.sub("[^0-9]", "", quant.name)
            code += quant_name[-9:].zfill(9)
            control_digit = upc.upc_calculate(code)
            code += control_digit
            quant.sscc_code = code

    weight = fields.Float(
        compute='_compute_weight',
        help="Weight computed based on the sum of the weights of the products."
    )
    sscc_code = fields.Char(string="SSCC", compute=_get_sscc)

    