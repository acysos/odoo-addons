# -*- encoding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2018  Acysos S.L.
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    crm_action_count = fields.Integer(compute='_compute_crm_action_count',
                                      string='# of CRM Actions')
    crm_action_ids = fields.One2many('crm.action', 'partner_id', 'CRM Actions')

    def _compute_crm_action_count(self):
        action_data = self.env['crm.action'].read_group(
            domain=[('partner_id', 'child_of', self.ids)],
            fields=['partner_id'], groupby=['partner_id'])
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict(
            [(m['partner_id'][0], m['partner_id_count']) for m in action_data])
        for partner in self:
            partner_ids = [r for r in partner_child_ids if r['id'] == partner.id][0]
            partner_ids = [partner_ids.get(
                'id')] + partner_ids.get('child_ids')
            partner.crm_action_count = sum(
                mapped_data.get(child, 0) for child in partner_ids)
