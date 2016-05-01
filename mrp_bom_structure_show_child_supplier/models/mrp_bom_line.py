# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    @api.one
    def _compute_standard_price(self):
        if self.product_id.seller_ids:
            if self.product_id.seller_ids[0].pricelist_ids:
                plist = self.product_id.seller_ids[0].pricelist_ids[0]
                template_std_price = plist.price
                if template_std_price == 0:
                    # This is in case not price defined in supplier pricelist
                    template_std_price = self.product_id.standard_price
                self.standard_price = template_std_price
            else:
                super(MrpBomLine, self)._compute_standard_price()
        else:
            super(MrpBomLine, self)._compute_standard_price()
