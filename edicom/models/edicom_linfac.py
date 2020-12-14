# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from .file_export import FileExport
import codecs


class EdicomLinfac(models.Model, FileExport):
    _name = "edicom.linfac"
    _description = "Detalle de la factura"

    factura_edicom_id = fields.Many2one(
        comodel_name='edicom.factura', string='Factura Edicom')
    NUMFAC = fields.Char(string='NUMFAC', size=15, required=True)
    NUMLIN = fields.Integer(string='NUMLIN', required=True)
    REFEAN = fields.Char(string='REFEAN', size=17, required=True)
    REFCLI = fields.Char(string='REFCLI', size=35)
    REFPRO = fields.Char(string='REFPRO', size=35)
    VP = fields.Char(string='VP', size=2)
    DUN14 = fields.Char(string='DUN14', size=14)
    DESC = fields.Char(string='DESC', size=70, required=True)
    CFAC = fields.Float(string='CFAC', required=True)
    MEDIDA = fields.Integer(string='MEDIDA')
    UMEDIDA = fields.Char(string='UMEDIDA', size=3)
    PRECIOB = fields.Float(string='PRECIOB', required=True)
    PRECION = fields.Float(string='PRECION', required=True)
    TIPOIMP1 = fields.Char(string='TIPOIMP1', size=3)
    TASAIMP1 = fields.Float(string='TASAIMP1')
    IMPTASA1 = fields.Float(string='IMPTASA1')
    TIPOIMP2 = fields.Char(string='TIPOIMP2', size=3)
    TASA2 = fields.Float(string='TASA2')
    IMPTASA2 = fields.Float(string='IMPTASA2')
    TIPOIMP3 = fields.Char(string='TIPOIMP3', size=3)
    TASA3 = fields.Float(string='TASA3')
    IMPTASA3 = fields.Float(string='IMPTASA3')
    CALIF1 = fields.Char(string='CALIF1', size=3)
    SECUEN1 = fields.Integer(string='SECUEN1')
    TIPO1 = fields.Char(string='TIPO1', size=3)
    PORCEN1 = fields.Float(string='PORCEN1')
    IMPDTO1 = fields.Float(string='IMPDTO1')
    CALIF2 = fields.Char(string='CALIF2', size=3)
    SECUEN2 = fields.Integer(string='SECUEN2')
    TIPO2 = fields.Char(string='TIPO2', size=3)
    PORCEN2 = fields.Float(string='PORCEN2')
    IMPDTO2 = fields.Float(string='IMPDTO2')
    CALIF3 = fields.Char(string='CALIF3', size=3)
    SECUEN3 = fields.Integer(string='SECUEN3')
    TIPO3 = fields.Char(string='TIPO3', size=3)
    PORCEN3 = fields.Float(string='PORCEN3')
    IMPDTO3 = fields.Float(string='IMPDTO3')
    CALIF4 = fields.Char(string='CALIF4', size=3)
    SECUEN4 = fields.Integer(string='SECUEN4')
    TIPO4 = fields.Char(string='TIPO4', size=3)
    PORCEN4 = fields.Float(string='PORCEN4')
    IMPDTO4 = fields.Float(string='IMPDTO4')
    CBONI = fields.Integer(string='CBONI')
    NETO = fields.Float(string='NETO', required=True)
    PVERDE = fields.Float(string='PVERDE', required=True)
    PEDIDO = fields.Char(string='PEDIDO', size=17)
    ALBARAN = fields.Char(string='ALBARAN', size=17)
    LOTE = fields.Char(string='LOTE', size=17)

    _rec_name = 'DESC'

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
        ['NUMLIN', 5, 0],
        ['REFEAN', 17],
        ['REFCLI', 35],
        ['REFPRO', 35],
        ['VP', 2],
        ['DUN14', 14],
        ['DESC', 70],
        ['CFAC', 5, 3],
        ['MEDIDA', 10, 0],
        ['UMEDIDA', 35],
        ['PRECIOB', 5, 3],
        ['PRECION', 5, 3],
        ['TIPOIMP1', 35],
        ['TASAIMP1', 8, 3],
        ['IMPTASA1', 5, 3],
        ['TIPOIMP2', 35],
        ['TASA2', 8, 3],
        ['IMPTASA2', 5, 3],
        ['TIPOIMP3', 35],
        ['TASA3', 8, 3],
        ['IMPTASA3', 5, 3],
        ['CALIF1', 35],
        ['SECUEN1', 2, 0],
        ['TIPO1', 35],
        ['PORCEN1', 8, 3],
        ['IMPDTO1', 5, 3],
        ['CALIF2', 35],
        ['SECUEN2', 2, 0],
        ['TIPO2', 35],
        ['PORCEN2', 8, 3],
        ['IMPDTO2', 5, 3],
        ['CALIF3', 35],
        ['SECUEN3', 2, 0],
        ['TIPO3', 35],
        ['PORCEN3', 8, 3],
        ['IMPDTO3', 5, 3],
        ['CALIF4', 35],
        ['SECUEN4', 2, 0],
        ['TIPO4', 35],
        ['PORCEN4', 8, 3],
        ['IMPDTO4', 5, 3],
        ['CBONI', 15, 0],
        ['NETO', 5, 3],
        ['PVERDE', 5, 3],
        ['PEDIDO', 17],
        ['ALBARAN', 17],
        ['LOTE', 17],
    ]

    @api.multi
    def generar(self, factura_edi):
        seq_pool = self.env['ir.sequence']
        journal_pool = self.env['account.journal']
        sale_obj = self.env['sale.order']

        linfac_ids = []
        factura = factura_edi.invoice_id
        if factura.partner_id.parent_id:
            partner = factura.partner_id.parent_id
        else:
            partner = factura.partner_id

        for line in factura_edi.invoice_id.invoice_line_ids:

            # ALBARAN Y PEDIDO DESDE ORIGEN
            pedidos = []
            albaranes = []
            text_pedidos = ''
            text_albaranes = ''
            # -- Prefijo de albaran
#             picking_seq = seq_pool.search([('code', '=', 'stock.picking.out')])
#             picking_prefix = seq_pool.read(
#                 picking_seq[0], ['prefix'])['prefix']
            # -- Prefijo de pedidos de venta
#             sale_seq = seq_pool.search([('code', '=', 'sale.order')])
#             sale_prefix = seq_pool.read(picking_seq[0], ['prefix'])['prefix']
            # -- Array de documentos de origen
#             sale_ids = sale_obj.search([('invoice_ids', 'in', factura.id)])
            sale_order_ids = []
            for sale_line in line.sale_line_ids:
                if sale_line.order_id.id not in sale_order_ids:
                    sale_order_ids.append(sale_line.order_id.id)
            sale_ids = sale_obj.browse(sale_order_ids)
#             origin = factura.origin.replace('-',',').replace(':',',').split(',')
#             for doc in origin:
#                 if (doc[0:len(picking_prefix)-1] == picking_prefix) and (doc not in albaranes):
#                     albaranes.append(doc)
#                 if (doc[0:len(sale_prefix)-1] == sale_prefix) and (doc not in pedidos):
#                     pedidos.append(doc)
            # -- Array --> String de documentos de origen
            for sale in sale_ids:
                if sale.client_order_ref:
                    text_pedidos += sale.client_order_ref
#             for albaran in albaranes:
#                 text_albaranes += albaran

            # PRECIO NETO
            precio_neto = round(
                line.price_unit * (1-line.discount/100),
                partner.edicom_decimal)

            line_number = line.line_number

            partner_barcode = line.product_id.ean13_ids.filtered(
                lambda ean13: ean13.partner_id == partner)
            if partner_barcode:
                refean = partner_barcode[0].name
            else:
                raise UserError(_(
                    'Not EAN Code for this product and this partner'))
#                 refean = line.product_id.barcode
#             refean = line.product_id.barcode

            data = {
                'factura_edicom_id': factura_edi.id,
                'NUMFAC': line.invoice_id.number,
                'NUMLIN': line_number,
                'REFEAN': refean,
                'DESC': line.product_id.name,
                'CFAC': line.quantity,
                'PRECIOB': line.price_unit,
                'PRECION': precio_neto,
                'NETO': round(
                    line.price_unit * line.quantity, partner.edicom_decimal),
#                 'NETO': round((
#                     line.price_unit * line.quantity)*(1-line.discount/100),
#                     partner.edicom_decimal),
#                     'PVERDE': line.total_extra_price,
                'PVERDE': 0,
                'REFCLI': text_pedidos,
                'ALBARAN': factura.origin,
                'UMEDIDA': 'PCE'
            }

            # IMPUESTOS
            i = 1
            for tax in line.invoice_line_tax_ids:
                if i > 3:
                    continue
                impuesto = {
                    'TIPOIMP'+str(i): 'VAT',
#                     'TASAIMP'+str(i): tax.amount * 100,
                    'TASAIMP'+str(i): tax.amount,
                    'IMPTASA'+str(i): tax.amount * data['NETO'],
                }
                data.update(impuesto)
                i = +1

            # DESCUENTO
            if line.discount and line.discount > 0:
                descuento = {
                    'CALIF1': 'A',
                    'SECUEN1': 1,
                    'TIPO1': 'TD',
                    'PORCEN1': line.discount,
                    'IMPDTO1': round((line.discount/100 * line.price_unit *
                                line.quantity), partner.edicom_decimal),
                }
                data.update(descuento)
                data['NETO'] = round(
                    data['NETO'] * (
                        1-line.discount/100), partner.edicom_decimal)
            if line.discount2 and line.discount2 > 0:
                descuento2 = {
                    'CALIF2': 'A',
                    'SECUEN2': 1,
                    'TIPO2': 'TD',
                    'PORCEN2': line.discount2,
                    'IMPDTO2': round((line.discount2/100 * line.price_unit *
                                line.quantity), partner.edicom_decimal),
                }
                data.update(descuento2)
                data['NETO'] = round(
                    data['NETO'] * (
                        1-line.discount2/100), partner.edicom_decimal)
            if line.discount3 and line.discount3 > 0:
                descuento3 = {
                    'CALIF3': 'A',
                    'SECUEN3': 1,
                    'TIPO3': 'TD',
                    'PORCEN3': line.discount3,
                    'IMPDTO3': round((line.discount3/100 * line.price_unit *
                                line.quantity), partner.edicom_decimal),
                }
                data.update(descuento3)
                data['NETO'] = round(
                    data['NETO'] * (
                        1-line.discount3/100), partner.edicom_decimal)

#             if factura.global_discount_ids:
#                 num_disc = 4
#                 for discount in factura.global_discount_ids:
#                     descuento_global = {
#                         'CALIF' + str(num_disc): 'A',
#                         'SECUEN' + str(num_disc): 1,
#                         'TIPO' + str(num_disc): 'TD',
#                         'PORCEN' + str(num_disc): discount.discount,
#                         'IMPDTO' + str(num_disc): (
#                             discount.discount/100 * line.price_unit * 
#                             line.quantity),
#                     }
#                     data.update(descuento_global)
#                     data['NETO'] = round(
#                         data['NETO'] * (
#                             1-discount.discount/100), partner.edicom_decimal)
#                     num_disc += 1
            linfac_ids.append(self.create(data))

        return linfac_ids

    def exportar(
            self, linfac_ids, path, file_suffix, out_char_sep):
        linfac_text = ''
        for linfac in linfac_ids:
                linfac_text += self.generate_txt(linfac, out_char_sep)
        outputFile = codecs.open(
            path + "/LINFAC_" + file_suffix+".txt", "w", "iso-8859-1")
        outputFile.write(linfac_text)
        outputFile.close()
        return True
