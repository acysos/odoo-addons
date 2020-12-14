# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from .file_export import FileExport
import codecs


class EdicomObsfac(models.Model, FileExport):
    _name = "edicom.obsfac"
    _description = "Observaciones de la factura"

    factura_edicom_id = fields.Many2one(
        comodel_name='edicom.factura', sting='Factura Edicom')
    NUMFAC = fields.Char(string='NUMFAC', size=15, required=True)
    NUMOBS = fields.Integer(string='NUMOBS', required=True)
    TEMA = fields.Char(string='REFCLI', size=3)
    TEXTO1 = fields.Char(string='TEXTO1', size=70, required=True)
    TEXTO2 = fields.Char(string='TEXTO2', size=70)
    TEXTO3 = fields.Char(string='TEXTO3', size=70)
    TEXTO4 = fields.Char(string='TEXTO4', size=70)
    TEXTO5 = fields.Char(string='TEXTO5', size=70)

    _rec_name = 'TEXTO1'

    """
    Array to store field sizes. Format: ['field_name', field_size,
    field_decimals]
    WARNING: Only set decimals for numeric fields! (will be filled with zeroes
    in IAPI creation
        string field example: 'test string' => ['example_field', 15] =>
        will output 'test_string    '
        int field example: 34  => ['example_int', 4, 0] =>
        will output: '0034'
        float field example: 2.5 => ['example_float', 13, 6] =>
        will output: '000002.500000'

    To fill integer field with spaces instead of zeroes declare it as string.
    Example:
        34 => ['example_int', 4] => will output '34  '
    FIELDS MUST BE DECLARED FOLLOWING EXACTLY THE IAPO ORDER
    """
    _sizes = [
        ['NUMFAC', 15],
        ['NUMOBS', 5, 0],
        ['TEMA', 3],
        ['TEXTO1', 70],
        ['TEXTO2', 70],
        ['TEXTO3', 70],
        ['TEXTO4', 70],
        ['TEXTO5', 70],
    ]

    @api.multi
    def generar(self, factura_edi):
        seq_pool = self.env['ir.sequence']
        journal_pool = self.env['account.journal']

        obsfac_id = False
        factura = factura_edi.invoice_id

        if factura_edi.invoice_id.comment:
            comment = factura_edi.invoice_id.comment
            comment_length = len(comment)
            data = {
                'factura_edicom_id': factura_edi.id,
                'NUMFAC': factura_edi.invoice_id.number,
                'NUMOBS': 0,
                'TEMA': 'AAI',
            }
            if comment_length <= 70:
                data.update({'TEXTO1': comment})
            else:
                data.update({'TEXTO1': comment[0:69]})
                if comment_length <= 140:
                    data.update({'TEXTO2': comment[70:]})
                else:
                    data.update({'TEXTO2': comment[70:139]})
                    if comment_length <= 210:
                        data.update({'TEXTO3': comment[140:]})
                    else:
                        data.update({'TEXTO3': comment[140:209]})
                        if comment_length <= 280:
                            data.update({'TEXTO4': comment[210:]})
                        else:
                            data.update({'TEXTO4': comment[210:279]})
                            if comment_length <= 350:
                                data.update({'TEXTO5': comment[280:]})
                            else:
                                data.update({'TEXTO5': comment[280:349]})

            obsfac_id = self.create(data)

        return obsfac_id

    @api.multi
    def exportar(
            self, obsfac_ids, path, file_suffix, out_char_sep):
        obsfac_text = ''
        for obsfac in obsfac_ids:
                obsfac_text += self.generate_txt(obsfac, out_char_sep)
        outputFile = codecs.open(
            path+"/OBSFAC_" + file_suffix + ".txt", "w", "iso-8859-1")
        outputFile.write(obsfac_text)
        outputFile.close()
        return True
