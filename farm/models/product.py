# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class Template(models.Model):
    _inherit = 'product.template'

    farrowing_price = fields.Float(string='Farrowing Price', digits=(16, 4),
                                   help=('Unitary cost for farrowing events.'
                                         'It\'s only used when the product is'
                                         'a group product of a farm specie.'))
    wearing_price = fields.Float(string='Weaning Price', digits=(16, 4),
                                 help=('Unitary cost for weaning events.'
                                       'It\'s only used when the product is a'
                                       'group product of a farm specie.'))
