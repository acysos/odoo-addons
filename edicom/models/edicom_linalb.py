# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from .file_export import FileExport
import time
import codecs
import pytz

EDICOM_UDM = {
    'kg': 'KGM',
    'gr': 'GRM',
    'liter(s)': 'LTR',
    'unit(s)': 'PCE',
    'm': 'MTR'
}

class EdicomLinalb(models.Model, FileExport):
    _name = "edicom.linalb"
    _description = "Detalle de la albaran"

    albaran_edicom_id = fields.Many2one(
        comodel_name='edicom.albaran', string='Albaran Edicom')
    IDCAB = fields.Char(string='IDCAB', size=10, required=True)
    IDEMB = fields.Char(string='IDEMB', size=10, required=True)
    IDLIN = fields.Char(string='IDLIN', size=10, required=True)
    EAN = fields.Char(string='EAN', size=35, required=True)
    VP = fields.Char(string='VP', size=2, required=True)
    REFPROV = fields.Char(string='REFPROV', size=35, required=True)
    REFCLI = fields.Char(string='REFCLI', size=35, required=True)
    SERIE = fields.Char(string='SERIE', size=35)
    NUMEXP = fields.Char(string='NUMEXP', size=35, required=True)
    DESCRIP = fields.Char(string='DESCRIP', size=70, required=True)
    TIPART = fields.Char(string='TIPART', size=3, required=True)
    CENVFAC = fields.Float(string='CENVFAC', required=True)
    CENVGRA = fields.Float(string='CENVGRA')
    CANGRUSU = fields.Float(string='CANGRUSU')
    CUEXP = fields.Float(string='CUEXP', required=True)
    UNICANT = fields.Char(string='UNICANT', size=3, required=True)
    TEXTO1 = fields.Char(string='TEXTO1', size=70)
    TEXTO2 = fields.Char(string='TEXTO2', size=70)
    TEXTO3 = fields.Char(string='TEXTO3', size=70)
    TEXTO4 = fields.Char(string='TEXTO4', size=70)
    TEXTO5 = fields.Char(string='TEXTO5', size=70)
    NUMPED = fields.Char(string='NUMPED', size=35, required=True)
    NUMALB = fields.Char(string='NUMALB', size=35, required=True)
    SSCC1 = fields.Char(string='SSCC1', size=35)
    SSCC2 = fields.Char(string='SSCC2', size=35)
    SSCC3 = fields.Char(string='SSCC3', size=35)
    SSCC4 = fields.Char(string='SSCC4', size=35)
    SSCC5 = fields.Char(string='SSCC5', size=35)
    FECENV = fields.Char(string='FECENV', size=12)
    FECCON = fields.Char(string='FECCON', size=12)
    LOTE = fields.Char(string='LOTE', size=35, required=True)
    CANTLOTE = fields.Float(string='CANTLOTE')
    LUGAR1 = fields.Char(string='LUGAR1', size=17)
    FECLOC1 = fields.Char(string='FECLOC1', size=12)
    CANTLOC1 = fields.Float(string='CANTLOC1')
    LUGAR2 = fields.Char(string='LUGAR2', size=17)
    FECLOC2 = fields.Char(string='FECLOC2', size=12)
    CANTLOC2 = fields.Float(string='CANTLOC2')
    LUGAR3 = fields.Char(string='LUGAR3', size=17)
    FECLOC3 = fields.Char(string='FECLOC3', size=12)
    CANTLOC3 = fields.Float(string='CANTLOC3')
    DESTINO = fields.Char(string='DESTINO', size=17)
    FECPED = fields.Char(string='FECPED', size=12)
    FECALB = fields.Char(string='FECALB', size=12)
    NUMLINPED = fields.Float(string='NUMLINPED')
    NUMLINALB = fields.Float(string='NUMLINALB')
    PESTOTLIN = fields.Float(string='PESTOTLIN')
    CANTPED = fields.Float(string='CANTPED')
    UNICANTPED = fields.Char(string='UNICANTPED', size=3)
    NUMCROTAL = fields.Char(string='NUMCROTAL', size=35)
    TARIFA = fields.Char(string='TARIFA', size=35)
    FECMAT = fields.Char(string='FECMAT', size=12)
    FECCAD = fields.Char(string='FECCAD', size=12, required=True)
    FECCONPR = fields.Char(string='FECCONPR', size=12)
    REGMATADERO = fields.Char(string='REGMATADERO', size=35)
    REGDESPIECE = fields.Char(string='REGDESPIECE', size=35)
    MATADERO = fields.Char(string='MATADERO', size=25)
    DESPIECE = fields.Char(string='DESPIECE', size=25)
    PNACIMIENTO = fields.Char(string='PNACIMIENTO', size=3)
    PORIGEN = fields.Char(string='PORIGEN', size=3)
    PCEBADO = fields.Char(string='PCEBADO', size=3)
    PMATANZA = fields.Char(string='PMATANZA', size=3)
    PELABORACION = fields.Char(string='PELABORACION', size=3)
    PDESPIECE = fields.Char(string='PDESPIECE', size=3)
    FECFABET = fields.Char(string='FECFABET', size=12)
    FECCADET = fields.Char(string='FECCADET', size=12)
    PESOBRUTO = fields.Float(string='PESOBRUTO')
    PESONETO = fields.Float(string='PESONETO')
    URLPUBLICADOR = fields.Char(string='URLPUBLICADOR', size=150)
    FECHABAJA = fields.Char(string='FECHABAJA', size=12)
    FECHANACIMIENTO = fields.Char(string='FECHANACIMIENTO', size=12)
    REGSALAENVASADO = fields.Char(string='REGSALAENVASADO', size=35)
    IDSALAENVASADO = fields.Char(string='IDSALAENVASADO', size=17)
    CATEGORIA = fields.Char(string='CATEGORIA', size=35)
    FECHACONFECCION = fields.Char(string='FECHACONFECCION', size=12)
    CANTIDADUE = fields.Float(string='CANTIDADUE')
    FECHAALTA = fields.Char(string='FECHAALTA', size=12)
    FECMATET = fields.Char(string='FECMATET', size=12)
    NOMLOC1 = fields.Char(string='NOMLOC1', size=70)
    NOMLOC2 = fields.Char(string='NOMLOC2', size=70)
    NOMLOC3 = fields.Char(string='NOMLOC3', size=70)
    NOMDESTINO = fields.Char(string='NOMDESTINO', size=70)
    PROPMERC = fields.Char(string='PROPMERC', size=35)
    PBRUTOLOTE = fields.Float(string='PBRUTOLOTE')
    PNETOLOTE = fields.Float(string='PNETOLOTE')
    UMEDIDAPES = fields.Char(string='UMEDIDAPES', size=3)
    EANCONT = fields.Char(string='EANCONT', size=35)
    PNETOUNIT = fields.Float(string='PNETOUNIT')
    UPNETOUNIT = fields.Char(string='UPNETOUNIT', size=3)
    ALTURA = fields.Float(string='ALTURA')
    LONGITUD = fields.Float(string='LONGITUD')
    PROFUND = fields.Float(string='PROFUND')
    UMEDIDA = fields.Char(string='UMEDIDA', size=3)
    CADUCTOT = fields.Float(string='CADUCTOT')
    CADUCMIN = fields.Float(string='CADUCMIN')
    PESTOTBRULIN = fields.Float(string='PESTOTBRULIN')
    RELLOC1 = fields.Char(string='RELLOC1', size=25)
    RELLOC2 = fields.Char(string='RELLOC2', size=25)
    RELLOC3 = fields.Char(string='RELLOC3', size=25)
    RELDESTINO = fields.Char(string='RELDESTINO', size=25)
    ISBN = fields.Char(string='ISBN', size=35)
    QVRCANT = fields.Float(string='QVRCANT')
    QVRCOD = fields.Char(string='QVRCOD', size=3)
    QVRMOTIVO = fields.Char(string='QVRMOTIVO', size=35)
    CANTDEV = fields.Float(string='CANTDEV')
    NUMPEDCLILIN = fields.Char(string='NUMPEDCLILIN', size=35)

    _rec_name = 'IDLIN'

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
        ['IDEMB', 10],
        ['IDLIN', 10],
        ['EAN', 35],
        ['VP', 2],
        ['REFPROV', 35],
        ['REFCLI', 35],
        ['SERIE', 35],
        ['NUMEXP', 35],
        ['DESCRIP', 70],
        ['TIPART', 3],
        ['CENVFAC', 15, 3],
        ['CENVGRA', 15, 3],
        ['CANGRUSU', 15, 3],
        ['CUEXP', 15, 3],
        ['UNICANT', 3],
        ['TEXTO1', 70],
        ['TEXTO2', 70],
        ['TEXTO3', 70],
        ['TEXTO4', 70],
        ['TEXTO5', 70],
        ['NUMPED', 35],
        ['NUMALB', 35],
        ['SSCC1', 35],
        ['SSCC2', 35],
        ['SSCC3', 35],
        ['SSCC4', 35],
        ['SSCC5', 35],
        ['FECENV', 12],
        ['FECCON', 12],
        ['LOTE', 35],
        ['CANTLOTE', 15, 3],
        ['LUGAR1', 17],
        ['FECLOC1', 12],
        ['CANTLOC1', 15, 3],
        ['LUGAR2', 17],
        ['FECLOC2', 12],
        ['CANTLOC2', 15, 3],
        ['LUGAR3', 17],
        ['FECLOC3', 12],
        ['CANTLOC3', 15, 3],
        ['DESTINO', 17],
        ['FECPED', 12],
        ['FECALB', 12],
        ['NUMLINPED', 15, 3],
        ['NUMLINALB', 15, 3],
        ['PESTOTLIN', 15, 3],
        ['CANTPED', 15, 3],
        ['UNICANTPED', 3],
        ['NUMCROTAL', 35],
        ['TARIFA', 35],
        ['FECMAT', 12],
        ['FECCAD', 12],
        ['FECCONPR', 12],
        ['REGMATADERO', 35],
        ['REGDESPIECE', 35],
        ['MATADERO', 25],
        ['DESPIECE', 25],
        ['PNACIMIENTO', 3],
        ['PORIGEN', 3],
        ['PCEBADO', 3],
        ['PMATANZA', 3],
        ['PELABORACION', 3],
        ['PDESPIECE', 3],
        ['FECFABET', 12],
        ['FECCADET', 12],
        ['PESOBRUTO', 15, 3],
        ['PESONETO', 15, 3],
        ['URLPUBLICADOR', 150],
        ['FECHABAJA', 12],
        ['FECHANACIMIENTO', 12],
        ['REGSALAENVASADO', 35],
        ['IDSALAENVASADO', 17],
        ['CATEGORIA', 35],
        ['FECHACONFECCION', 12],
        ['CANTIDADUE', 15, 3],
        ['FECHAALTA', 12],
        ['FECMATET', 12],
        ['NOMLOC1', 70],
        ['NOMLOC2', 70],
        ['NOMLOC3', 70],
        ['NOMDESTINO', 70],
        ['PROPMERC', 35],
        ['PBRUTOLOTE', 15, 3],
        ['PNETOLOTE', 15, 3],
        ['UMEDIDAPES', 3],
        ['EANCONT', 35],
        ['PNETOUNIT', 15, 3],
        ['UPNETOUNIT', 3],
        ['ALTURA', 15, 3],
        ['LONGITUD', 15, 3],
        ['PROFUND', 15, 3],
        ['UMEDIDA', 3],
        ['CADUCTOT', 15, 3],
        ['CADUCMIN', 15, 3],
        ['PESTOTBRULIN', 15, 3],
        ['RELLOC1', 25],
        ['RELLOC2', 25],
        ['RELLOC3', 25],
        ['RELDESTINO', 25],
        ['ISBN', 35],
        ['QVRCANT', 15, 3],
        ['QVRCOD', 3],
        ['QVRMOTIVO', 35],
        ['CANTDEV', 15, 3],
        ['NUMPEDCLILIN', 35],
    ]

    @api.multi
    def generar(self, albaran_edi):
        custinfo_obj = self.env['product.customerinfo']
        linalb_ids = []
        albaran = albaran_edi.picking_id

        if albaran.partner_id.parent_id:
            partner = albaran.partner_id.parent_id
        else:
            partner = albaran.partner_id

        num_lin = 1

        for line in albaran.move_line_ids.filtered(
                lambda l: l.qty_done > 0):
            custinfo = custinfo_obj.search(
                [('name', '=', partner.id),
                 ('product_id', '=', line.product_id.id)])
            if custinfo:
                refcli = custinfo[0].product_code
            else:
                refcli = False
            unicant = 'PCE'
            if line.product_uom_id.name.lower() in EDICOM_UDM:
                unicant = EDICOM_UDM[line.product_uom_id.name.lower()]
            if not line.result_package_id and not line.package_id:
                raise UserError(_('You can export to EDI without package'))
            if not line.move_id.product_packaging:
                raise UserError(_(
                    'You can export to EDI without a line packaging'))
            tz_name = pytz.timezone(
                self.env.context.get('tz') or record.env.user.tz)
        
            partner_barcode = line.product_id.ean13_ids.filtered(
                lambda ean13: ean13.partner_id == partner)
            if partner_barcode:
                ean = partner_barcode[0].name
            else:
                raise UserError(_(
                    'Not EAN Code for this product and this partner'))
#                 ean = line.product_id.barcode
#             ean = line.product_id.barcode

            data = {
                'albaran_edicom_id': albaran_edi.id,
                'IDCAB': str(albaran.id),
                'IDEMB': (line.result_package_id.name or line.package_id.name)[-10:],
                'IDLIN': str(num_lin),
                'EAN': ean,
                'VP': '',
                'REFPROV': line.product_id.default_code or '',
                'REFCLI': refcli or '',
                'NUMEXP': '',
                'DESCRIP': line.product_id.name,
                'TIPART': line.product_id.edicom_tipart or 'CU',
#                 'CENVFAC': line.move_id.sale_line_id.qty_invoiced,
                'CENVFAC': line.qty_done,
                'CUEXP': line.move_id.product_packaging.qty,
                'UNICANT': unicant,
                'NUMPED': albaran.sale_id.name,
                'NUMALB': albaran.name,
                'FECCON': line.lot_id.use_date.astimezone(tz_name).strftime('%Y%m%d'),
            }
            feccad = ''
            feccadet = ''
            lote = ''
            if line.lot_id:
                lote = line.lot_id.name
                if line.lot_id.life_date:
                    feccad = line.lot_id.life_date.astimezone(tz_name).strftime('%Y%m%d')
                    feccadet = line.lot_id.life_date.astimezone(tz_name).strftime('%Y%m%d')
                elif line.lot_id.use_date:
                    feccad = line.lot_id.use_date.astimezone(tz_name).strftime('%Y%m%d')
                    feccadet = line.lot_id.use_date.astimezone(tz_name).strftime('%Y%m%d')
                data['LOTE'] = lote
                data['FECCAD'] = feccad
                data['FECCADET'] = feccadet
            num_lin += 1
            linalb_ids.append(self.create(data))

        return linalb_ids

    def exportar(
            self, linalb_ids, path, file_suffix, out_char_sep):
        linalb_text = ''
        for linalb in linalb_ids:
                linalb_text += self.generate_txt(linalb, out_char_sep)
        outputFile = codecs.open(
            path + "/LINALB_" + file_suffix+".txt", "w", "iso-8859-1")
        outputFile.write(linalb_text)
        outputFile.close()
        return True




