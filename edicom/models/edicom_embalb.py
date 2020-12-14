# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from .file_export import FileExport
import time
import codecs

EDICOM_UDM = {
    'kg': 'KGM',
    'gr': 'GRM',
    'liter(s)': 'LTR',
    'unit(s)': 'PCE',
    'm': 'MTR'
}

class EdicomEmbalb(models.Model, FileExport):
    _name = "edicom.embalb"
    _description = "Embalajes de la albaran"

    albaran_edicom_id = fields.Many2one(
        comodel_name='edicom.albaran', string='Albaran Edicom')
    IDCAB = fields.Char(string='IDCAB', size=10, required=True)
    IDEMB = fields.Char(string='IDEMB', size=10, required=True)
    CPS = fields.Char(string='CPS', size=12, required=True)
    CPSPADRE = fields.Char(string='CPSPADRE', size=12, required=True)
    CANTEMB = fields.Float(string='CANTEMB', required=True)
    TIPCOD = fields.Char(string='TIPCOD', size=3)
    COSEMB = fields.Char(string='COSEMB', size=3)
    TIPEMB = fields.Char(string='TIPEMB', size=3)
    DESCEMB = fields.Char(string='DESCEMB', size=35)
    PAGRET = fields.Char(string='PAGRET', size=3)
    PESON = fields.Float(string='PESON')
    PESOB = fields.Float(string='PESOB')
    PESOBU = fields.Float(string='PESOBU')
    PESONU = fields.Float(string='PESONU')
    UPESO = fields.Char(string='UPESO', size=3)
    ALTURA = fields.Float(string='ALTURA')
    LONGITUD = fields.Float(string='LONGITUD')
    ANCHURA = fields.Float(string='ANCHURA')
    UMEDIDA = fields.Char(string='UMEDIDA', size=3)
    CANCONSI = fields.Float(string='CANCONSI')
    MANIPUL = fields.Char(string='MANIPUL', size=3)
    DESCMANI = fields.Char(string='DESCMANI', size=70)
    SSCC1 = fields.Char(string='SSCC1', size=35)
    SSCC2 = fields.Char(string='SSCC2', size=35)
    SSCC3 = fields.Char(string='SSCC3', size=35)
    SSCC4 = fields.Char(string='SSCC4', size=35)
    SSCC5 = fields.Char(string='SSCC5', size=35)
    LOTE = fields.Char(string='LOTE', size=35)
    TIPO2 = fields.Char(string='TIPO2', size=3)
    TCAJAS = fields.Float(string='TCAJAS')
    DESTDIF = fields.Char(string='DESTDIF', size=3)
    FECMAT = fields.Char(string='FECMAT', size=12)
    FECCAD = fields.Char(string='FECCAD', size=12)
    FECCON = fields.Char(string='FECCON', size=12)
    VOLUMEN = fields.Float(string='VOLUMEN')
    BULTFORM = fields.Float(string='BULTFORM')
    BULTPALET = fields.Float(string='BULTPALET')
    FORMATO = fields.Char(string='FORMATO', size=3)
    NUMFORMATO = fields.Float(string='NUMFORMATO')
    NUMCAPAS = fields.Float(string='NUMCAPAS')
    GRAI = fields.Char(string='GRAI', size=35)
    REFTRANS = fields.Char(string='REFTRANS', size=35)
    FECREFTRANS = fields.Char(string='FECREFTRANS', size=12)

    _sizes = [
        ['IDCAB', 10],
        ['IDEMB', 10],
        ['CPS', 12],
        ['CPSPADRE', 12],
        ['CANTEMB', 15, 3],
        ['TIPCOD', 3],
        ['COSEMB', 3],
        ['TIPEMB', 3],
        ['DESCEMB', 35],
        ['PAGRET', 3],
        ['PESON', 15, 3],
        ['PESOB', 15, 3],
        ['PESONU', 15, 3],
        ['PESOBU', 15, 3],
        ['UPESO', 3],
        ['ALTURA', 15, 3],
        ['LONGITUD', 15, 3],
        ['ANCHURA', 15, 3],
        ['UMEDIDA', 3],
        ['CANCONSI', 15, 3],
        ['MANIPUL', 3],
        ['DESCMANI', 70],
        ['SSCC1', 35],
        ['SSCC2', 35],
        ['SSCC3', 35],
        ['SSCC4', 35],
        ['SSCC5', 35],
        ['LOTE', 35],
        ['TIPO2', 3],
        ['TCAJAS', 15, 3],
        ['DESTDIF', 3],
        ['FECMAT', 12],
        ['FECCAD', 12],
        ['FECCON', 12],
        ['VOLUMEN', 15, 3],
        ['BULTFORM', 15, 3],
        ['BULTPALET', 15, 3],
        ['FORMATO', 3],
        ['NUMFORMATO', 15, 3],
        ['NUMCAPAS', 15, 3],
        ['GRAI', 35],
        ['REFTRANS', 35],
        ['FECREFTRANS', 12],
    ]

    @api.multi
    def generar(self, albaran_edi):
        embalb_ids = []
        albaran = albaran_edi.picking_id
        num_cps = 1
        packages = albaran.move_line_ids.mapped('result_package_id')
        data_init = {
            'albaran_edicom_id': albaran_edi.id,
            'IDCAB': str(albaran.id),
            'IDEMB': 'CPSPADRE',
            'CPS': str(num_cps),
            'CPSPADRE': '',
            'CANTEMB': len(packages),
            'TIPEMB': '201',
            'SSCC1': albaran.sscc_code,
        }

        num_cps += 1
        embalb_ids.append(self.create(data_init))
        for package in packages:
            line_env = self.env['stock.move.line']
            if len(package.quant_ids) > 0:
                data = {
                    'albaran_edicom_id': albaran_edi.id,
                    'IDCAB': str(albaran.id),
                    'IDEMB': package.name[-10:],
                    'CPS': str(num_cps),
                    'CPSPADRE': 1,
                    'CANTEMB': len(package.quant_ids),
                    'TIPEMB': package.packaging_id.shipper_package_code or 'CT',
                    'DESCEMB': package.packaging_id.name or '',
                    'PESON': package.weight or '',
                    'PESOB': package.weight or '',
                    'UPESO': 'KGM',
                    'ALTURA': package.packaging_id.height or '',
                    'LONGITUD': package.packaging_id.length or '',
                    'ANCHURA': package.packaging_id.width or '',
                    'UMEDIDA': 'CMT',
                    'SSCC1': package.sscc_code,
                }
                num_cps += 1
                embalb_ids.append(self.create(data))

        return embalb_ids

    def exportar(
            self, linalb_ids, path, file_suffix, out_char_sep):
        linalb_text = ''
        for linalb in linalb_ids:
                linalb_text += self.generate_txt(linalb, out_char_sep)
        outputFile = codecs.open(
            path + "/EMBALB_" + file_suffix+".txt", "w", "iso-8859-1")
        outputFile.write(linalb_text)
        outputFile.close()
        return True





    