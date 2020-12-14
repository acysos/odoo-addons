# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
from odoo import _, api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    edicom_tipo_impuesto = fields.Selection(
        string='Tipo EDI',
        selection=[
            ('VAT', 'IVA'),
            ('ENV', 'Envases y residuos'),
            ('EXT', 'Exento'),
            ('IGI', 'IGIC (Impuesto de las Islas Canarias)'),
            ('ACT', 'Impuesto de alcoholes'),
            ('RE', 'Recargo de Equivalencia'),
            ('RET', 'Retenciones por servicios profesionales'),
            ('OTH', 'Otros Impuestos'),
        ],
        default='VAT'
    )

    @api.multi
    def get_tipo_impuesto_by_name(self, name):
        code = ''
        tax_ids = self.search([('name', '=', name)])
        if tax_ids:
            edicom_tipo_impuesto = self.read(
                tax_ids[0].id,
                ['edicom_tipo_impuesto']
            )['edicom_tipo_impuesto']
            code = edicom_tipo_impuesto or ''
        return code
