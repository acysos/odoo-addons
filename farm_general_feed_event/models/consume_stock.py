# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.connector.queue.job import job
    from openerp.addons.connector.session import ConnectorSession
except ImportError:
    _logger.debug('Can not `import connector`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory


class ConsumeStock(models.Model):
    _inherit = 'farm.consume.stock'

    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('progress', 'In progress'),
                                        ('confirmed', 'Confirmed')],
                             default='draft')

    @api.multi
    def long_confirm(self):
        for res in self:
            res.state = 'progress'
            session = ConnectorSession.from_env(self.env)
            confirm_consume_stock.delay(session, 'farm.consume.stock', res.id)


@job(default_channel='root.farm.consume.stock')
def confirm_consume_stock(session, model_name, order_id):
    model = session.env[model_name]
    order = model.browse(order_id)
    order.confirm()
    session.cr.commit()
