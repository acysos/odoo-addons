# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.exceptions import Warning

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.onchange('barcode')
    def barcode_scanning(self):
        match = False
        pack_obj = self.env['product.packaging']
        package_ids = pack_obj.search([('barcode', '=', self.barcode)])
        if len(package_ids) > 1:
            raise Warning('More that one package with this barcode')
        if package_ids and self.barcode:
            package = package_ids[0]
            product = package.product_id
            if self.barcode and self.move_lines:
                for line in self.move_lines:
                    if line.product_id.barcode == product.barcode:
                        line.quantity_done += package.qty
                        self.barcode = None
                        match = True
        if not match:
            super(StockPicking, self).barcode_scanning()
