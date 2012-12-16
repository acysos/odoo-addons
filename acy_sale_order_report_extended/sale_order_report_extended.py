##############################################################################
#  
#    Copyright (C) 2004-2010 Yannick Soldati. All Rights Reserved
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
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

from osv import osv
from osv import fields


class sale_order_report_extended(osv.osv):
    _name = 'sale.order.report.extended'

    def _short_name(self, cr, uid, ids, names, arg, context):
        
        return dict(self.name_get(cr, uid, ids, context))

    _columns = {
        'text': fields.text('Text', translate=True),
        'name': fields.char('Name', size=64, required=False, readonly=False),
        'short_name': fields.function(_short_name, method=True, type='char', 
                                      string='Name'),
    }

    def name_get(self, cr, user, ids, context=None):
        return [(x.id, x.name.splitlines()[0]) for x in
                self.browse(cr, user, ids, context=context)]

sale_order_report_extended()


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def onchange_text(self, cr, uid, ids, report_id, partner_id, company_id):
        context = {}
        partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
        context['lang'] = partner.lang
        company = self.pool.get('res.company').browse(cr,uid,company_id)
        report = self.pool.get('sale.order.report.extended').browse(cr,uid,report_id,context)
        text = report.text
        if text:
            text = text.replace("[[company]]",company.name).replace("[[partner]]",partner.name)
        return text

    def onchange_header(self, cr, uid, ids, report_id, partner_id, company_id):
        text = self.onchange_text(cr,uid,ids,report_id, partner_id, company_id)
        return {'value': {'header_related': text}}
    def onchange_footer(self, cr, uid, ids, report_id, partner_id, company_id):
        text = self.onchange_text(cr,uid,ids,report_id, partner_id, company_id)
        return {'value': {'footer_related': text}}
    def onchange_options(self, cr, uid, ids, report_id, partner_id, company_id):
        text = self.onchange_text(cr,uid,ids,report_id, partner_id, company_id)
        return {'value': {'options_related': text}}
    def onchange_special(self, cr, uid, ids, report_id, partner_id, company_id):
        text = self.onchange_text(cr,uid,ids,report_id, partner_id, company_id)
        return {'value': {'special_sale_conditions_related': text}}

    _columns = {
        'header_id':fields.many2one('sale.order.report.extended', 'Header'),
        'footer_id':fields.many2one('sale.order.report.extended', 'Footer'),
        'options_id':fields.many2one('sale.order.report.extended', 'Options'),
        'special_sale_conditions_id':fields.many2one(
                                'sale.order.report.extended', 
                                'Special sale conditions'),

        'header_related': fields.text('Header',multi="report.extended"),
        'footer_related': fields.text('Footer',multi="report.extended"),
        'options_related': fields.text('Options',multi="report.extended"),
        'special_sale_conditions_related': fields.text('Special sale conditions',multi="report.extended"),
    }
sale_order()
