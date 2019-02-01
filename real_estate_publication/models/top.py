# -*- encoding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
#           Daniel Pascal <daniel@acysos.com>
# Copyright (C) 2013  Acysos S.L.

from openerp import models, fields, api, _
import base64
import os
import ftplib
import magic

class real_estate_top_press_publication(models.Model):
    _name = 'real.estate.top.press.publication'
    
    date = fields.Date('Date', required=True)
    page = fields.Integer('Page')
    press_id = fields.Many2one('res.partner', 'Press', ondelete='cascade')
    _order = 'date'

class real_estate_top_press(models.Model):
    _name = 'real.estate.top.press'
    
    name = fields.Char('Press', required=True, size=64)
    actual = fields.Boolean('Active', default=lambda *a: 1)
    date_publications = fields.One2many('real.estate.top.press.publication',
                                        'press_id','Date Publications')
    top_id = fields.Many2one('real.estate.top', 'Top', ondelete='cascade')
    _order = 'name'
    

class real_estate_top_internet_wo(models.Model):
    _name = 'real.estate.top.internet.wo'
    
    name = fields.Char('Website', required=True, size=64)
    actual = fields.Boolean('Active', default=lambda *a: 1)
    top_id = fields.Many2one('real.estate.top', 'Top', ondelete='cascade')
    _order = 'name'
    

class real_estate_top(models.Model):
    _inherit = 'real.estate.top'
    
    publications = fields.One2many(comodel_name='real.estate.top.press',
                                   inverse_name='top_id',string='Publications')
    #'web_url':fields.Char('Web URL', size=64, required=False, readonly=False)
    internet_wo = fields.One2many(comodel_name='real.estate.top.internet.wo',
                                inverse_name='top_id',
                                string='Internet WO Update')
    poster = fields.Boolean('Poster')
    internet_description = fields.Html('Internet Description', translate=True)
    #energy_doc_url = fields.Char('Energy URL', size=512)
    
    
    
    
    