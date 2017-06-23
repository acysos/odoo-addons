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
import base64
import os
import ftplib
import magic

class real_state_top_press_publication(models.Model):
    _name = 'real.state.top.press.publication'
    
    date = fields.Date('Date', required=True)
    page = fields.Integer('Page')
    press_id = fields.Many2one('res.partner', 'Press', ondelete='cascade')
    _order = 'date'

class real_state_top_press(models.Model):
    _name = 'real.state.top.press'
    
    name = fields.Char('Press', required=True, size=64)
    actual = fields.Boolean('Active', default=lambda *a: 1)
    date_publications = fields.One2many('real.state.top.press.publication',
                                        'press_id','Date Publications')
    top_id = fields.Many2one('real.state.top', 'Top', ondelete='cascade')
    _order = 'name'
    

class real_state_top_internet_wo(models.Model):
    _name = 'real.state.top.internet.wo'
    
    name = fields.Char('Website', required=True, size=64)
    actual = fields.Boolean('Active', default=lambda *a: 1)
    top_id = fields.Many2one('real.state.top', 'Top', ondelete='cascade')
    _order = 'name'
    

class real_state_top(models.Model):
    _inherit = 'real.state.top'
    
    publications = fields.One2many(comodel_name='real.state.top.press',
                                   inverse_name='top_id',string='Publications')
    #'web_url':fields.Char('Web URL', size=64, required=False, readonly=False)
    internet_wo = fields.One2many(comodel_name='real.state.top.internet.wo',
                                inverse_name='top_id',
                                string='Internet WO Update')
    poster = fields.Boolean('Poster')
    internet_description = fields.Text('Internet Description')
    #energy_doc_url = fields.Char('Energy URL', size=512)
    
    
    
    
    