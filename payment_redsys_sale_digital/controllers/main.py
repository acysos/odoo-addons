# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.payment_redsys.controllers.main import RedsysController

_logger = logging.getLogger(__name__)


class RedsysController(RedsysController):

    @http.route(
        ['/payment/redsys/result/<page>'], type='http', auth='user',
        methods=['GET'], website=True)
    def redsys_result(self, page, **vals):
        response = super(RedsysController, self).redsys_result(page=page, **vals)
        if not 'order' in response.qcontext:
            return response
        order_products_attachments = {}
        order = response.qcontext['order']
        invoiced_lines = request.env['account.invoice.line'].sudo().search(
            [('invoice_id', 'in', order.invoice_ids.ids),
             ('invoice_id.state', '=', 'paid')])

        purchased_products_attachments = {}
        for il in invoiced_lines:
            p_obj = il.product_id
            # Ignore products that do not have digital content
            if not p_obj.product_tmpl_id.type == 'digital':
                continue

            # Search for product attachments
            A = request.env['ir.attachment']
            p_id = p_obj.id
            template = p_obj.product_tmpl_id
            att = A.search_read(
                domain=['|', '&', ('res_model', '=', p_obj._name),
                        ('res_id', '=', p_id), '&',
                        ('res_model', '=', template._name),
                        ('res_id', '=', template.id)],
                fields=['name', 'write_date'],
                order='write_date desc',
            )

            # Ignore products with no attachments
            if not att:
                continue

            purchased_products_attachments[p_id] = att

        response.qcontext.update({
            'digital_attachments': purchased_products_attachments,
        })
        return response

