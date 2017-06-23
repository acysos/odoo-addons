# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#                       Daniel Pascal <daniel@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _

class real_state_cities(models.Model):
    _name = 'real.state.cities'
    city_id = fields.Many2one('res.better.zip')


class real_state_top(models.Model):
    _inherit = 'real.state.top'
    
    website_published = fields.Boolean('Publish in Real State')
    website_featured = fields.Boolean('Outstanding top')
    website_opportunity = fields.Boolean('Opportunity')
    original_sale_price = fields.Float('Original Sale Price')
    original_rent_price = fields.Float('Original Rent Price')
    website_actsta = fields.Selection([
            ('none','None'),
            ('pending_sold','Pending Sold'),
            ('pending_rented','Pending Rented'),
            ('sold','Sold'),
            ('rented','Rented'),
             ],    'State', select=True, readonly=False)

    @api.model
    def create(self, vals):
        res = super(real_state_top, self).create(vals)
        if not self.env['real.state.cities'].search(
                [('city_id', '=', res.city_id.id)]):
            self.env['real.state.cities'].create({'city_id': res.city_id.id})
        return res
    
    @api.multi
    def write(self, vals):
        if 'city_id' in vals:
            for top in self:
                if not self.env['real.state.cities'].search(
                    [('city_id', '=', top.city_id.id)]):
                    self.env['real.state.cities'].create({'city_id': top.city_id.id})
        super(real_state_top, self).write(vals)
        return True
            
            