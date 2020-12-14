# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from .file_export import FileExport
import time
import codecs


class EdicomCabalb(models.Model, FileExport):
    _name = "edicom.cabalb"
    _description = "Cabecera del albaran"

    albaran_edicom_id = fields.Many2one(
        comodel_name='edicom.albaran', string='Albaran Edicom')
    IDCAB = fields.Char(string='IDCAB', size=10, required=True)
    NUMDES = fields.Char(string='NUMDES', size=35, required=True)
    TIPO = fields.Char(string='TIPO', size=3, required=True, default='351')
    FUNCION = fields.Char(string='FUNCION', size=3, required=True, default='9')
    FECDES = fields.Char(string='FECDES', size=12, required=True)
    FECENT = fields.Char(string='FECENT', size=12, required=True)
    FECENTSO = fields.Char(string='FECENTSO', size=12, required=True)
    FECPANT = fields.Char(string='FECPANT', size=12)
    FECPDES = fields.Char(string='FECPDES', size=12)
    CONESP = fields.Char(string='CONESP', size=3)
    NUMALB = fields.Char(string='NUMALB', size=35, required=True)
    FECALB = fields.Char(string='FECALB', size=12, required=True)
    NUMPED = fields.Char(string='NUMPED', size=35, required=True)
    FECPED = fields.Char(string='FECPED', size=12, required=True)
    NUMPICK = fields.Char(string='NUMPICK', size=35)
    FECPICK = fields.Char(string='FECPICK', size=12)
    ORIGEN = fields.Char(string='ORIGEN', size=17, required=True)
    DESTINO = fields.Char(string='DESTINO', size=17, required=True)
    PROVEEDO = fields.Char(string='PROVEEDO', size=17, required=True)
    COMPRADO = fields.Char(string='COMPRADO', size=17, required=True)
    DPTO = fields.Char(string='DPTO', size=17, required=True)
    RECEPTOR = fields.Char(string='RECEPTOR', size=17, required=True)
    MUELLE = fields.Char(string='MUELLE', size=17, required=True)
    PUNTENV = fields.Char(string='PUNTENV', size=17)
    EXPEDIDO = fields.Char(string='EXPEDIDO', size=17)
    ULTCONS = fields.Char(string='ULTCONS', size=17)
    ENTREGA = fields.Char(string='ENTREGA', size=3)
    REPOS = fields.Char(string='REPOS', size=35)
    PORTES = fields.Char(string='PORTES', size=3)
    RECOGIDA = fields.Char(string='RECOGIDA', size=3)
    TIPTRANS = fields.Char(string='TIPTRANS', size=3, required=True)
    IDTRANS = fields.Char(string='IDTRANS', size=17, required=True)
    MATRIC = fields.Char(string='MATRIC', size=35, required=True)
    TOTQTY = fields.Float(string='TOTQTY', required=True)
    IDENTIF = fields.Char(string='IDENTIF', size=3)
    CONSIG = fields.Char(string='CONSIG', size=3)
    CIP = fields.Char(string='CIP', size=17)
    FECENVIO = fields.Char(string='FECENVIO', size=12)
    CODPROV = fields.Char(string='CODPROV', size=25)
    NUMPLAENT = fields.Char(string='NUMPLAENT', size=35)
    NOMBREEMISOR = fields.Char(string='NOMBREEMISOR', size=70)
    NIFEMISOR = fields.Char(string='NIFEMISOR', size=17)
    NOMBRERECEPTOR = fields.Char(string='NOMBRERECEPTOR', size=70)
    NIFRECEPTOR = fields.Char(string='NIFRECEPTOR', size=17)
    NOMBRECOMPRADOR = fields.Char(string='NOMBRECOMPRADOR', size=70)
    NOMBREPROVEEDOR = fields.Char(string='NOMBREPROVEEDOR', size=70)
    NOMBREPTOENTREGA = fields.Char(string='NOMBREPTOENTREGA', size=70)
    URLPUBLICADOR = fields.Char(string='URLPUBLICADOR', size=150)
    NUMCONTRATO = fields.Char(string='NUMCONTRATO', size=35)
    ALTA_BAJA = fields.Char(string='ALTA/BAJA', size=1)
    DIRECCIONEMISOR = fields.Char(string='DIRECCIONEMISOR', size=70)
    POBLACIONEMISOR = fields.Char(string='POBLACIONEMISOR', size=35)
    PROVINCIAEMISOR = fields.Char(string='PROVINCIAEMISOR', size=35)
    CPEMISOR = fields.Char(string='CPEMISOR', size=35)
    DIRECCIONCOMPRADOR = fields.Char(string='DIRECCIONCOMPRADOR', size=70)
    POBLACIONCOMPRADOR = fields.Char(string='POBLACIONCOMPRADOR', size=35)
    PROVINCIACOMPRADOR = fields.Char(string='PROVINCIACOMPRADOR', size=35)
    CPCOMPRADOR = fields.Char(string='CPCOMPRADOR', size=35)
    DIRECCIONPROVEEDOR = fields.Char(string='DIRECCIONPROVEEDOR', size=70)
    POBLACIONPROVEEDOR = fields.Char(string='POBLACIONPROVEEDOR', size=35)
    PROVINCIAPROVEEDOR = fields.Char(string='PROVINCIAPROVEEDOR', size=35)
    CPPROVEEDOR = fields.Char(string='CPPROVEEDOR', size=35)
    NOMBREPTOEMISION = fields.Char(string='NOMBREPTOEMISION', size=70)
    DIRECCIONPTOEMISION = fields.Char(string='DIRECCIONPTOEMISION', size=70)
    POBLACIONPTOEMISION = fields.Char(string='POBLACIONPTOEMISION', size=35)
    PROVINCIAPTOEMISION = fields.Char(string='PROVINCIAPTOEMISION', size=35)
    CPPTOEMISION = fields.Char(string='CPPTOEMISION', size=35)
    DIRECCIONPTOENTREGA = fields.Char(string='DIRECCIONPTOENTREGA', size=70)
    POBLACIONPTOENTREGA = fields.Char(string='POBLACIONPTOENTREGA', size=35)
    PROVINCIAPTOENTREGA = fields.Char(string='PROVINCIAPTOENTREGA', size=35)
    CPPTOENTREGA = fields.Char(string='CPPTOENTREGA', size=35)
    NOMBRETRANSPORTISTA = fields.Char(string='NOMBRETRANSPORTISTA', size=70)
    NOMBRECONSIGNATARIO = fields.Char(string='NOMBRECONSIGNATARIO', size=70)
    DIRECCIONRECEPTOR = fields.Char(string='DIRECCIONRECEPTOR', size=70)
    POBLACIONRECEPTOR = fields.Char(string='POBLACIONRECEPTOR', size=35)
    PROVINCIARECEPTOR = fields.Char(string='PROVINCIARECEPTOR', size=35)
    CPRECEPTOR = fields.Char(string='CPRECEPTOR', size=35)
    NIFPROVEEDOR = fields.Char(string='NIFPROVEEDOR', size=17)
    IMPTOTBRUTO = fields.Float(string='IMPTOTBRUTO')
    IMPTOTNETO = fields.Float(string='IMPTOTNETO')
    MONEDA = fields.Char(string='MONEDA', size=3)
    FECSAL = fields.Char(string='FECSAL', size=12)
    FECSALEST = fields.Char(string='FECSALEST', size=12)
    NOMCONREC = fields.Char(string='NOMCONREC', size=35)
    PESBRUTOT = fields.Float(string='PESBRUTOT')
    PESNETTOT = fields.Float(string='PESNETTOT')
    NUMTOTBUL = fields.Float(string='NUMTOTBUL')
    CONEMB = fields.Char(string='CONEMB', size=35)
    FECCONEMB = fields.Char(string='FECCONEMB', size=12)
    REFTRANS = fields.Char(string='REFTRANS', size=35)
    FECREFTRANS = fields.Char(string='FECREFTRANS', size=12)
    PAISPROVEEDOR = fields.Char(string='PAISPROVEEDOR', size=3)
    PAISCOMPRADOR = fields.Char(string='PAISCOMPRADOR', size=3)
    PAISPTOENTREGA = fields.Char(string='PAISPTOENTREGA', size=3)
    ETAPATRANS = fields.Char(string='ETAPATRANS', size=3)
    MEDIOTRANS = fields.Char(string='MEDIOTRANS', size=3)
    CONDENTREG = fields.Char(string='CONDENTREG', size=35)
    PAISPUNTENV = fields.Char(string='PAISPUNTENV', size=3)
    CLIENTE = fields.Char(string='CLIENTE', size=17)
    PAGADOR = fields.Char(string='PAGADOR', size=17)
    CODPAIS = fields.Char(string='CODPAIS', size=70)
    NOMCONTACTOPROV = fields.Char(string='NOMCONTACTOPROV', size=35)
    EMAILCONTACTPROV = fields.Char(string='EMAILCONTACTPROV', size=50)
    TELCONTACTPROV = fields.Char(string='TELCONTACTPROV', size=15)
    FAXCONTACTPROV = fields.Char(string='FAXCONTACTPROV', size=15)
    WWWCONTACTPROV = fields.Char(string='WWWCONTACTPROV', size=100)
    NUMPEDCOM = fields.Char(string='NUMPEDCOM', size=35)
    NUMPEDREAP = fields.Char(string='NUMPEDREAP', size=35)
    ORDENADOR = fields.Char(string='ORDENADOR', size=17)
    NUMPEDCLI = fields.Char(string='NUMPEDCLI', size=35)
    TEMPERATURA = fields.Float(string='TEMPERATURA')
    TOTENTREGA = fields.Float(string='TOTENTREGA')

    _rec_name = 'NUMDES'

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
        ['IDCAB', 10],
        ['NUMDES', 35],
        ['TIPO', 3],
        ['FUNCION', 3],
        ['FECDES', 12],
        ['FECENT', 12],
        ['FECENTSO', 12],
        ['FECPANT', 12],
        ['FECPDES', 12],
        ['CONESP', 3],
        ['NUMALB', 35],
        ['FECALB', 12],
        ['NUMPED', 35],
        ['FECPED', 12],
        ['NUMPICK', 35],
        ['FECPICK', 12],
        ['ORIGEN', 17],
        ['DESTINO', 17],
        ['PROVEEDO', 17],
        ['COMPRADO', 17],
        ['DPTO', 17],
        ['RECEPTOR', 17],
        ['MUELLE', 17],
        ['PUNTENV', 17],
        ['EXPEDIDO', 17],
        ['ULTCONS', 17],
        ['ENTREGA', 3],
        ['REPOS', 35],
        ['PORTES', 3],
        ['RECOGIDA', 3],
        ['TIPTRANS', 3],
        ['IDTRANS', 17],
        ['MATRIC', 35],
        ['TOTQTY', 15, 3],
        ['IDENTIF', 3],
        ['CONSIG', 3],
        ['CIP', 17],
        ['FECENVIO', 12],
        ['CODPROV', 25],
        ['NUMPLAENT', 35],
        ['NOMBREEMISOR', 70],
        ['NIFEMISOR', 17],
        ['NOMBRERECEPTOR', 70],
        ['NIFRECEPTOR', 17],
        ['NOMBRECOMPRADOR', 70],
        ['NOMBREPROVEEDOR', 70],
        ['NOMBREPTOENTREGA', 70],
        ['URLPUBLICADOR', 150],
        ['NUMCONTRATO', 35],
        ['ALTA_BAJA', 1],
        ['DIRECCIONEMISOR', 70],
        ['POBLACIONEMISOR', 35],
        ['PROVINCIAEMISOR', 35],
        ['CPEMISOR', 35],
        ['DIRECCIONCOMPRADOR', 70],
        ['POBLACIONCOMPRADOR', 35],
        ['PROVINCIACOMPRADOR', 35],
        ['CPCOMPRADOR', 35],
        ['DIRECCIONPROVEEDOR', 70],
        ['POBLACIONPROVEEDOR', 35],
        ['PROVINCIAPROVEEDOR', 35],
        ['CPPROVEEDOR', 35],
        ['NOMBREPTOEMISION', 70],
        ['DIRECCIONPTOEMISION', 70],
        ['POBLACIONPTOEMISION', 35],
        ['PROVINCIAPTOEMISION', 35],
        ['CPPTOEMISION', 35],
        ['DIRECCIONPTOENTREGA', 70],
        ['POBLACIONPTOENTREGA', 35],
        ['PROVINCIAPTOENTREGA', 35],
        ['CPPTOENTREGA', 35],
        ['NOMBRETRANSPORTISTA', 70],
        ['NOMBRECONSIGNATARIO', 70],
        ['DIRECCIONRECEPTOR', 70],
        ['POBLACIONRECEPTOR', 35],
        ['PROVINCIARECEPTOR', 35],
        ['CPRECEPTOR', 35],
        ['NIFPROVEEDOR', 17],
        ['IMPTOTBRUTO', 15, 3],
        ['IMPTOTNETO', 15, 3],
        ['MONEDA', 3],
        ['FECSAL', 12],
        ['FECSALEST', 12],
        ['NOMCONREC', 35],
        ['PESBRUTOT', 15, 3],
        ['PESNETTOT', 15, 3],
        ['NUMTOTBUL', 15, 3],
        ['CONEMB', 35],
        ['FECCONEMB', 12],
        ['REFTRANS', 35],
        ['FECREFTRANS', 12],
        ['PAISPROVEEDOR', 3],
        ['PAISCOMPRADOR', 3],
        ['PAISPTOENTREGA', 3],
        ['ETAPATRANS', 3],
        ['MEDIOTRANS', 3],
        ['CONDENTREG', 35],
        ['PAISPUNTENV', 3],
        ['CLIENTE', 17],
        ['PAGADOR', 17],
        ['CODPAIS', 70],
        ['NOMCONTACTOPROV', 35],
        ['EMAILCONTACTPROV', 50],
        ['TELCONTACTPROV', 15],
        ['FAXCONTACTPROV', 15],
        ['WWWCONTACTPROV', 100],
        ['NUMPEDCOM', 35],
        ['NUMPEDREAP', 35],
        ['ORDENADOR', 17],
        ['NUMPEDCLI', 35],
        ['TEMPERATURA', 15, 1],
        ['TOTENTREGA', 15, 0],
    ]

    @api.multi
    def generar(self, albaran_edi):
        albaran = albaran_edi.picking_id

        # FECHAS
        date = albaran.date.strftime('%Y%m%d')
        date_done = albaran.date_done.strftime('%Y%m%d')
        scheduled_date = albaran.scheduled_date.strftime('%Y%m%d')
        sale_date = albaran.sale_id.confirmation_date.strftime('%Y%m%d')
        if albaran.sale_id.commitment_date:
            commitent_date = albaran.sale_id.commitment_date.strftime('%Y%m%d')
        else:
            commitent_date = albaran.sale_id.expected_date.strftime('%Y%m%d')

#         if albaran.partner_id.parent_id:
#             partner = albaran.partner_id.parent_id
#         else:
#             partner = albaran.partner_id
        partner = albaran.partner_id
        data = {
            'albaran_edicom_id': albaran_edi.id,
            'IDCAB': str(albaran.id),
            'NUMDES': albaran.name,
            'FECDES': date,
            'FECENT': scheduled_date,
            'FECENTSO': commitent_date,
            'NUMALB': albaran.name,
            'FECALB': date_done,
            'NUMPED': albaran.sale_id.client_order_ref or albaran.sale_id.name,
            'FECPED': sale_date,
            'ORIGEN': albaran.company_id.partner_id.codigo_edi,
            'DESTINO': albaran.partner_id.codigo_edi,
            'PROVEEDO': albaran.company_id.partner_id.codigo_edi,
            'COMPRADO': partner.codigo_edi,
            'DPTO': albaran.sale_id.partner_invoice_id.codigo_edi,
            'RECEPTOR': albaran.partner_id.codigo_edi,
            'MUELLE': albaran.edicom_dock.codigo_edi or '',
#             'PORTES': albaran.edicom_portes or '',
#             'RECOGIDA': albaran.edicom_recogida or '',
            'TIPTRANS': albaran.edicom_tiptrans or '',
            'IDTRANS': albaran.edicom_idtrans.codigo_edi or '',
            'MATRIC': albaran.edicom_idtrans.edicom_matricula or '',
            'TOTQTY': albaran.edicom_totqty,
        }
        cabalb_id = self.create(data)
        return cabalb_id

    @api.multi
    def exportar(
            self, cabalb_ids, path, file_suffix, out_char_sep):
        cabalb_text = ''
        for cabalb in cabalb_ids:
                cabalb_text += self.generate_txt(cabalb, out_char_sep)
        outputFile = codecs.open(
            path + "/CABALB_" + file_suffix + ".txt", "w", "iso-8859-1")
        outputFile.write(cabalb_text)
        outputFile.close()
        return True
