# -*- coding: utf-8 -*-
# Copyright 2017 FactorLibre - Ismael Calvo <ismael.calvo@factorlibre.com>
# Copyright 2017 Ignacio Ibeas - Acysos S.L. <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from osv import osv, fields


class account_fiscal_position_template(osv.osv):
    _inherit = 'account.fiscal.position.template'

    _columns = {
        'sii_registration_key_sale': fields.many2one(
            'aeat.sii.mapping.registration.keys',
            "Default SII Resgistration Key for Sales",
            domain=[('type', '=', 'sale')]),
        'sii_registration_key_purchase': fields.many2one(
            'aeat.sii.mapping.registration.keys',
            "Default SII Resgistration Key for Purchases",
            domain=[('type', '=', 'purchase')])
    }
account_fiscal_position_template()


class account_fiscal_position(osv.osv):
    _inherit = 'account.fiscal.position'

    _columns = {
        'sii_registration_key_sale': fields.many2one(
            'aeat.sii.mapping.registration.keys',
            "Default SII Resgistration Key for Sales",
            domain=[('type', '=', 'sale')]),
        'sii_registration_key_purchase': fields.many2one(
            'aeat.sii.mapping.registration.keys',
            "Default SII Resgistration Key for Purchases",
            domain=[('type', '=', 'purchase')])
    }
account_fiscal_position()
