# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from .file_export import FileExport
import time
import codecs


class EdicomCabfac(models.Model, FileExport):
    _name = "edicom.cabfac"
    _description = "Cabecera de la factura"

    factura_edicom_id = fields.Many2one(
        comodel_name='edicom.factura', string='Factura Edicom')
    NUMFAC = fields.Char(string='NUMFAC', size=15, required=True)
    VENDEDOR = fields.Char(string='VENDEDOR', size=17, required=True)
    EMISOR = fields.Char(string='EMISOR', size=17, required=True)
    COBRADOR = fields.Char(string='COBRADOR', size=17)
    COMPRADOR = fields.Char(string='COMPRADOR', size=17, required=True)
    DEPTO = fields.Char(string='DEPTO', size=13)
    RECEPTOR = fields.Char(string='RECEPTOR', size=17, required=True)
    CLIENTE = fields.Char(string='CLIENTE', size=17, required=True)
    PAGADOR = fields.Char(string='PAGADOR', size=17)
    PEDIDO = fields.Char(string='PEDIDO', size=17, required=True)
    FECHA = fields.Char(string='FECHA', size=12, required=True)
    NODO = fields.Char(string='NODO', size=3)
    FUNCION = fields.Char(string='FUNCION', size=3)
    RSOCIAL = fields.Char(string='RSOCIAL', size=70, required=True)
    CALLE = fields.Char(string='CALLE', size=35, required=True)
    CIUDAD = fields.Char(string='CIUDAD', size=35, required=True)
    CP = fields.Integer(string='CP', required=True)
    NIF = fields.Char(string='NIF', size=17, required=True)
    RAZON = fields.Char(string='RAZON', size=3)
    ALBARAN = fields.Char(string='ALBARAN', size=17, required=True)
    CONTRATO = fields.Char(string='CONTRATO', size=17)
    NFACSUS = fields.Char(string='NFACSUS', size=17)
    FPAGO = fields.Char(string='FPAGO', size=3, default='60')
    DIVISA = fields.Char(string='DIVISA', size=3, default='EUR')
    SUMNETOS = fields.Float(string='SUMNETOS', required=True)
    SUMBRUTO = fields.Float(string='SUMBRUTO')
    CARGOS = fields.Float(string='CARGOS', required=True, default=0)
    DESCUEN = fields.Float(string='DESCUEN', required=True, default=0)
    BASEIMP1 = fields.Float(string='BASEIMP1', required=True)
    TIPOIMP1 = fields.Char(string='TIPOIMP1', size=3, required=True)
    TASAIMP1 = fields.Float(string='TASAIMP1', required=True)
    IMPIMP1 = fields.Float(string='IMPIMP1', required=True)
    BASEIMP2 = fields.Float(string='BASEIMP2')
    TIPOIMP2 = fields.Char(string='TIPOIMP2', size=3)
    TASAIMP2 = fields.Float(string='TASAIMP2')
    IMPIMP2 = fields.Float(string='IMPIMP2')
    BASEIMP3 = fields.Float(string='BASEIMP3')
    TIPOIMP3 = fields.Char(string='TIPOIMP3', size=3)
    TASAIMP3 = fields.Float(string='TASAIMP3')
    IMPIMP3 = fields.Float(string='IMPIMP3')
    BASEIMP4 = fields.Float(string='BASEIMP4')
    TIPOIMP4 = fields.Char(string='TIPOIMP4', size=3)
    TASAIMP4 = fields.Float(string='TASAIMP4')
    IMPIMP4 = fields.Float(string='IMPIMP4')
    BASEIMP5 = fields.Float(string='BASEIMP5')
    TIPOIMP5 = fields.Char(string='TIPOIMP5', size=3)
    TASAIMP5 = fields.Float(string='TASAIMP5')
    IMPIMP5 = fields.Float(string='IMPIMP5')
    BASEIMP6 = fields.Float(string='BASEIMP6')
    TIPOIMP6 = fields.Char(string='TIPOIMP6', size=3)
    TASAIMP6 = fields.Float(string='TASAIMP6')
    IMPIMP6 = fields.Float(string='IMPIMP6')
    BASEIMP = fields.Float(string='BASEIMP', required=True)
    TOTIMP = fields.Float(string='TOTIMP', required=True)
    TOTAL = fields.Float(string='TOTAL', required=True)
    VTO1 = fields.Char(string='VTO1', size=8, required=False)
    IMPVTO1 = fields.Float(string='IMPVTO1', required=False)
    VTO2 = fields.Char(string='VTO2', size=8)
    IMPVTO2 = fields.Float(string='IMPVTO2')
    VTO3 = fields.Char(string='VTO3', size=8)
    IMPVTO3 = fields.Float(string='IMPVTO3')
    TPVERDE = fields.Float(string='TPVERDE', required=True, default=0)
    CALIF1 = fields.Char(string='CALIF1', size=3)
    SECUEN1 = fields.Integer(string='SECUEN1')
    TIPO1 = fields.Char(string='TIPO1', size=3)
    PORCEN1 = fields.Float(string='PORCEN1')
    IMPDES1 = fields.Float(string='IMPDES1')
    CALIF2 = fields.Char(string='CALIF2', size=3)
    SECUEN2 = fields.Integer(string='SECUEN2')
    TIPO2 = fields.Char(string='TIPO2', size=3)
    PORCEN2 = fields.Float(string='PORCEN2')
    IMPDES2 = fields.Float(string='IMPDES2')
    CALIF3 = fields.Char(string='CALIF3', size=3)
    SECUEN3 = fields.Integer(string='SECUEN3')
    TIPO3 = fields.Char(string='TIPO3', size=3)
    PORCEN3 = fields.Float(string='PORCEN3')
    IMPDES3 = fields.Float(string='IMPDES3')
    CALIF4 = fields.Char(string='CALIF4', size=3)
    SECUEN4 = fields.Integer(string='SECUEN4')
    TIPO4 = fields.Char(string='TIPO4', size=3)
    PORCEN4 = fields.Float(string='PORCEN4')
    IMPDES4 = fields.Float(string='IMPDES4')
    CALIF5 = fields.Char(string='CALIF5', size=3)
    SECUEN5 = fields.Integer(string='SECUEN5')
    TIPO5 = fields.Char(string='TIPO5', size=3)
    PORCEN5 = fields.Float(string='PORCEN5')
    IMPDES5 = fields.Float(string='IMPDES5')
    ERSOCIAL = fields.Char(string='ERSOCIAL', size=70, required=True)
    ECALLE = fields.Char(string='ECALLE', size=35, required=True)
    EPOBLAC = fields.Char(string='EPOBLAC', size=35, required=True)
    ECP = fields.Integer(string='ECP', required=True)
    ENIF = fields.Char(string='ENIF', size=17, required=True)
    EMERCA = fields.Char(string='EMERCA', size=70, required=True)
    NOTAC = fields.Char(string='NOTAC', size=17)
    NUMREL = fields.Char(string='NUMREL', size=17)
    RECOGIDA = fields.Char(string='RECOGIDA', size=17)
    DESTINO = fields.Char(string='DESTINO', size=17)
    FECHAEFE = fields.Char(string='FECHAEFE', size=12)

    _rec_name = 'NUMFAC'

    """
    Array to store field sizes. Format: ['field_name', field_size,
    field_decimals]
    WARNING: Only set decimals for numeric fields! (will be filled with zeroes
    in IAPI creation
    string field example: 'test string' => ['example_field', 15] =>
    will output 'test_string    '
    int field example: 34  => ['example_int', 4, 0] => will output: '0034'
    float field example: 2.5 => ['example_float', 13, 6] =>
    will output: '000002.500000'

    To fill integer field with spaces instead of zeroes declare it as string.
    Example:
        34 => ['example_int', 4] => will output '34  '
    FIELDS MUST BE DECLARED FOLLOWING EXACTLY THE IAPO ORDER
    """
    _sizes = [
        ['NUMFAC', 15],
        ['VENDEDOR', 17],
        ['EMISOR', 17],
        ['COBRADOR', 17],
        ['COMPRADOR', 17],
        ['DEPTO', 13],
        ['RECEPTOR', 17],
        ['CLIENTE', 17],
        ['PAGADOR', 17],
        ['PEDIDO', 17],
        ['FECHA', 12],
        ['NODO', 3],
        ['FUNCION', 3],
        ['RSOCIAL', 70],
        ['CALLE', 35],
        ['CIUDAD', 35],
        ['CP', 5, 0],
        ['NIF', 17],
        ['RAZON', 3],
        ['ALBARAN', 17],
        ['CONTRATO', 17],
        ['NFACSUS', 17],
        ['FPAGO', 3],
        ['DIVISA', 3],
        ['SUMNETOS', 15, 3],
        ['SUMBRUTO', 15, 3],
        ['CARGOS', 15, 3],
        ['DESCUEN', 15, 3],
        ['BASEIMP1', 15, 3],
        ['TIPOIMP1', 3],
        ['TASAIMP1', 8, 3],
        ['IMPIMP1', 15, 3],
        ['BASEIMP2', 15, 3],
        ['TIPOIMP2', 3],
        ['TASAIMP2', 8, 3],
        ['IMPIMP2', 15, 3],
        ['BASEIMP3', 15, 3],
        ['TIPOIMP3', 3],
        ['TASAIMP3', 8, 3],
        ['IMPIMP3', 15, 3],
        ['BASEIMP4', 15, 3],
        ['TIPOIMP4', 3],
        ['TASAIMP4', 8, 3],
        ['IMPIMP4', 15, 3],
        ['BASEIMP5', 15, 3],
        ['TIPOIMP5', 3],
        ['TASAIMP5', 8, 3],
        ['IMPIMP5', 15, 3],
        ['BASEIMP6', 15, 3],
        ['TIPOIMP6', 3],
        ['TASAIMP6', 8, 3],
        ['IMPIMP6', 15, 3],
        ['BASEIMP', 15, 3],
        ['TOTIMP', 15, 3],
        ['TOTAL', 15, 3],
        ['VTO1', 8],
        ['IMPVTO1', 15, 3],
        ['VTO2', 8],
        ['IMPVTO2', 15, 3],
        ['VTO3', 8],
        ['IMPVTO3', 15, 3],
        ['TPVERDE', 15, 3],
        ['CALIF1', 3],
        ['SECUEN1', 2, 0],
        ['TIPO1', 3],
        ['PORCEN1', 8, 3],
        ['IMPDES1', 15, 3],
        ['CALIF2', 3],
        ['SECUEN2', 2, 0],
        ['TIPO2', 3],
        ['PORCEN2', 8, 3],
        ['IMPDES2', 15, 3],
        ['CALIF3', 3],
        ['SECUEN3', 2, 0],
        ['TIPO3', 3],
        ['PORCEN3', 8, 3],
        ['IMPDES3', 15, 3],
        ['CALIF4', 3],
        ['SECUEN4', 2, 0],
        ['TIPO4', 3],
        ['PORCEN4', 8, 3],
        ['IMPDES4', 15, 3],
        ['CALIF5', 3],
        ['SECUEN5', 2, 0],
        ['TIPO5', 3],
        ['PORCEN5', 8, 3],
        ['IMPDES5', 15, 3],
        ['ERSOCIAL', 70],
        ['ECALLE', 35],
        ['EPOBLAC', 35],
        ['ECP', 5, 0],
        ['ENIF', 17],
        ['EMERCA', 70],
        ['NOTAC', 17],
        ['NUMREL', 17],
        ['RECOGIDA', 17],
        ['DESTINO', 17],
        ['FECHAEFE', 12],
    ]

    @api.multi
    def generar(self, factura_edi):
        seq_pool = self.env['ir.sequence']
        journal_pool = self.env['account.journal']
        sale_obj = self.env['sale.order']

        cabfac = ''
        factura = factura_edi.invoice_id

        # FECHA
        fecha = factura.date_invoice.strftime('%Y%m%d')
        # CP
        try:
            cp = int(factura.partner_id.zip)
        except ValueError:
            cp = 0

        # ALBARAN Y PEDIDO DESDE ORIGEN
        pedidos = []
        albaranes = []
        text_pedidos = ''
        text_albaranes = ''
        # -- Prefijo de albaran
#         picking_seq = seq_pool.search([('code', 'like', 'stock.picking.out')])
#         picking_prefix = seq_pool.read(picking_seq[0], ['prefix'])['prefix']
        # -- Prefijo de pedidos de venta
#         sale_seq = seq_pool.search([('code', 'like', 'sale.order')])
#         sale_prefix = seq_pool.read(sale_seq[0], ['prefix'])['prefix']
        # -- Array de documentos de origen
        sale_ids = sale_obj.search([('invoice_ids', 'in', factura.id)])
#         origin = factura.origin.replace(':',',').split(',')
#         for doc in origin:
#             if (doc[0:len(picking_prefix)-1] == picking_prefix) and (doc not in albaranes):
#                 albaranes.append(doc)
#             if (doc[0:len(sale_prefix)-1] == sale_prefix) and (doc not in pedidos):
#                 pedidos.append(doc)
        # -- Array --> String de documentos de origen
        for sale in sale_ids:
            if sale.client_order_ref:
                text_pedidos += sale.client_order_ref
#         for albaran in albaranes:
#             text_albaranes += albaran
        nodo = factura.company_id.edi_node
        if factura.type == 'out_refund':
            nodo = factura.company_id.edi_node_out_refund

        if factura.partner_id.parent_id:
            partner = factura.partner_id.parent_id
        else:
            partner = factura.partner_id
        data = {
            'factura_edicom_id': factura_edi.id,
            'NUMFAC': factura.number,
            'VENDEDOR': factura.company_id.partner_id.codigo_edi,
            'EMISOR': factura.company_id.partner_id.codigo_edi,
            'COBRADOR': factura.company_id.partner_id.codigo_edi,
            'COMPRADOR': factura.partner_shipping_id.codigo_edi,
            'RECEPTOR': factura.partner_shipping_id.codigo_edi,
            'CLIENTE': partner.codigo_edi,
            'PAGADOR': partner.codigo_edi,
            'PEDIDO': factura.name,
            'FECHA': fecha,
            'NODO': nodo,
            'FUNCION': '9',
            'RSOCIAL': partner.name,
            'CALLE': partner.street,
            'CIUDAD': partner.city,
            'CP': cp,
            'NIF': partner.vat,
            'ALBARAN': factura.origin or '',
            'SUMNETOS': round(factura.amount_total, partner.edicom_decimal),
            'SUMBRUTO': round(factura.amount_untaxed, partner.edicom_decimal),
            'BASEIMP': round(factura.amount_untaxed, partner.edicom_decimal),
            'TOTIMP': round(factura.amount_tax, partner.edicom_decimal),
            'TOTAL': round(factura.amount_total, partner.edicom_decimal),
            'ERSOCIAL': factura.company_id.name,
            'ECALLE': factura.company_id.street,
            'EPOBLAC': factura.company_id.city,
            'ECP': factura.company_id.zip,
            'ENIF': factura.company_id.vat,
            'EMERCA': factura.company_id.company_registry,
            # 'TPVERDE': factura.total_extra_price
            'FECHAEFE': fecha,
            }

        # IMPUESTOS
        i = 1
        for tax in factura.tax_line_ids:
            if i > 6 or i > len(factura.tax_line_ids):
                continue
            impuesto = {
                'BASEIMP'+str(i): tax.base,
                'TIPOIMP'+str(i): 'VAT',
                'TASAIMP'+str(i): tax.tax_id.amount,
                'IMPIMP'+str(i): tax.amount,
            }
            data.update(impuesto)
            i += 1

        # VENCIMIENTOS
        moves = []
        if factura.move_id:
            for move_line in factura.move_id.line_ids:
                if move_line.account_id == factura.account_id:
                    moves.append(move_line)
            i = 1
            for move in moves:
                if i > 3:
                    continue
                date = move.date_maturity or factura.date_invoice
                fecha = date.strftime('%Y%m%d')
                vencimiento = {
                    # Fecha del primer Vencimiento (Formato YYYYMMDD)
                    'VTO' + str(i): fecha,
                    'IMPVTO' + str(i): move.debit,
                }
                data.update(vencimiento)
                i += 1
        cabfac_id = self.create(data)

        return cabfac_id

    @api.multi
    def exportar(
            self, cabfac_ids, path, file_suffix, out_char_sep):
        cabfac_text = ''
        for cabfac in cabfac_ids:
            cabfac_text += self.generate_txt(cabfac, out_char_sep)
        outputFile = codecs.open(
            path + "/CABFAC_" + file_suffix + ".txt", "w", "iso-8859-1")
        outputFile.write(cabfac_text)
        outputFile.close()
        return True
