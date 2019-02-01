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

class real_estate_cities(models.Model):
    _name = 'real.estate.cities'
    city_id = fields.Many2one('res.better.zip')


class real_estate_top(models.Model):
    _inherit = 'real.estate.top'

    @api.multi
    @api.depends(
        'sale_price', 'original_sale_price', 'rent_price',
        'original_rent_price')
    def _get_reduced_price(self):
        for top in self:
            if top.sale_price < top.original_sale_price or \
                    top.rent_price < top.original_rent_price:
                top.reduced_price = True
            else:
                top.reduced_price = False

    @api.multi
    @api.depends(
        'flat_heating', 'chalet_heating', 'office_heating',
        'shop_heating')
    def _get_heating(self):
        for top in self:
            if top.flat_heating or top.chalet_heating or top.office_heating \
                    or top.shop_heating:
                top.heating = True
            else:
                top.heating = False

    @api.multi
    @api.depends(
        'shop_air_conditioning', 'office_air_conditioning',
        'home_air_conditioning')
    def _get_airconditioning(self):
        for top in self:
            if top.home_air_conditioning or top.office_air_conditioning or \
                    top.shop_air_conditioning:
                top.airconditioning = True
            else:
                top.airconditioning = False

    website_published = fields.Boolean('Publish in Real Estate')
    website_featured = fields.Boolean('Outstanding top')
    website_opportunity = fields.Boolean('Opportunity')
    original_sale_price = fields.Float('Original Sale Price')
    original_rent_price = fields.Float('Original Rent Price')
    reduced_price = fields.Boolean(
        string='Reduced price', compute=_get_reduced_price, store=True)
    heating = fields.Boolean(string='Heating', compute=_get_heating, store=True)
    airconditioning = fields.Boolean(
        string='Air Conditioning', compute=_get_airconditioning, store=True)
#    changed by top_estate in sale_rental
#     website_actsta = fields.Selection([
#             ('none','None'),
#             ('pending_sold','Pending Sold'),
#             ('pending_rented','Pending Rented'),
#             ('sold','Sold'),
#             ('rented','Rented'),
#              ],    'State', select=True, readonly=False)

    @api.model
    def create(self, vals):
        res = super(real_estate_top, self).create(vals)
        if not self.env['real.estate.cities'].search(
                [('city_id', '=', res.city_id.id)]):
            self.env['real.estate.cities'].create({'city_id': res.city_id.id})
        return res

    @api.multi
    def write(self, vals):
        if 'city_id' in vals:
            for top in self:
                if not self.env['real.estate.cities'].search(
                    [('city_id', '=', top.city_id.id)]):
                    self.env['real.estate.cities'].create({'city_id': top.city_id.id})
        super(real_estate_top, self).write(vals)
        return True
            
            