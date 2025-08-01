# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>.
# Copyright (C) 2024 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class transformationEvent(models.Model):
    _inherit = 'farm.transformation.event'

    def move_group(self):
        super(transformationEvent, self).move_group()
        analy_ac_obj = self.env['account.analytic.account']
        new_farm = self.get_farm(self.to_location)
        top_account = analy_ac_obj.search([
            ('name', '=', new_farm.name)])
        if not top_account:
            gen_account = analy_ac_obj.search([
                ('name', '=', 'General Account')])
            if not gen_account:
                gen_account = analy_ac_obj.create({'name': 'General Account'})
            top_account = analy_ac_obj.create({'name': new_farm.name,
                                               'parent_id': gen_account.id})
            self.animal_group.account.parent_id = top_account