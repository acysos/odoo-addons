# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res['note'] = self.notes and self.notes or ''
        return res
