# Copyright 2022 Acysos - Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_sii_enabled(self):
        super(AccountMove, self)._compute_sii_enabled()
        for invoice in self:
            if invoice.company_id.sii_enabled and invoice.is_invoice():
                sale_orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
                for sale_order in sale_orders.filtered(
                        lambda sale: sale.amazon_channel != False):
                    if (sale_order.amazon_channel == 'fba' and
                            invoice.partner_id.country_id.id != invoice.company_id.country_id.id):
                        invoice.sii_enabled = False
                        _logger.info("SII FBA Amazon: " + invoice.name)