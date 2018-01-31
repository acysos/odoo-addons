# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2018  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _default_agents(self):
        print 'entra'
        print self.env.context
        agents = []
        delivery_ad = self.env.context.get('delivery_ad')
        print delivery_ad
        print self.env.context.get('partner_id')
        if delivery_ad != \
                self.env.context.get('partner_id'):
            for agent in self.env['res.partner'].browse(delivery_ad).agents:
                vals = {
                    'agent': agent.id,
                    'commission': agent.commission.id,
                }
                vals['display_name'] = self.env['sale.order.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
            if len(agents) != 0:
                return [(0, 0, x) for x in agents]
        return super(SaleOrderLine, self)._default_agents()

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name='sale.order.line.agent', inverse_name='sale_line',
        copy=True, readonly=True, default=_default_agents)
