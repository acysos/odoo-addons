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

class rental_agreement(models.Model):
    _name = 'rental.agreement'

    name = fields.Char('Reference', size=64, select=True, readonly=True)
    partner_id = fields.Many2one('res.partner',
        'Tenant',
        select=True,
        required=True,
        domain= [('real_estate_type','=','tenant')])
    signing_date = fields.Date('Signing date')
    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date', required=True)
    rent_price = fields.Float('Rent Price')
    notes = fields.Text('Notes')
    top_id = fields.Many2one('real.estate.top', 'Top', required=True, 
                             ondelete='cascade', select=True)
    owner_id = fields.Many2one('res.partner',
        'Owner',
        select=True,
        domain= [('real_estate_type','=','owner')])
    rent_attachments_url = fields.Char(string='Attachments URL')

    _order = 'start_date'

    @api.onchange('top_id')
    def onchange_top_id(self):
        if self.top_id:
            owner_id = self.top_id.partner_id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('rental.agreement')
        res = super(rental_agreement, self).create(vals)
        return res
