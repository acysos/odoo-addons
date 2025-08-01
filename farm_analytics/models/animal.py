# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>.
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class Animal(models.Model):
    _inherit = 'farm.animal'

    account = fields.Many2one('account.analytic.account', 'Analytic Account')


class Female(models.Model):
    _inherit = 'farm.animal'

    @api.model
    def create(self, vals):
        res = super(Female, self).create(vals)
        analy_ac_obj = self.env['account.analytic.account']
        top_account = analy_ac_obj.search([
            ('name', '=', res.farm.name)])
        if not top_account:
            gen_account = analy_ac_obj.search([
                ('name', '=', 'General Account')])
            if not gen_account:
                gen_account = analy_ac_obj.create({'name': 'General Account'})
            top_account = analy_ac_obj.create({'name': res.farm.name,
                                               'parent_id': gen_account.id})
        new_account = analy_ac_obj.create({
            'name': 'AA-'+res.type+'-'+res.number,
            'parent_id': top_account.id})
        res.account = new_account
        return res