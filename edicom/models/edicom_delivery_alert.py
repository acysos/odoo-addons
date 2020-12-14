# -*- coding: utf-8 -*-
# Copyright 2020 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, exceptions, _
import codecs


class EdicomDeliveryAlert(models.Model):
    _name = 'edicom.delivey.alert'


    @api.onchange('driver')
    def _onchange_partner(self):
        for alert in self:
            alert.driver_phone = alert.driver.phone or alert.driver.mobile
            alert.driver_vat = alert.driver.vat

    name = fields.Integer(string='Number', copy=False)
    date = fields.Date(string='Date', copy=False, default=fields.Date.today())
    date_sent = fields.Datetime(string='Date Sent', copy=False)
    driver = fields.Many2one(string='Driver', comodel_name='res.partner')
    driver_phone = fields.Char(string='Driver phone')
    driver_vat = fields.Char(string='Driver vat')
    driver_plate = fields.Char(string='Driver plate')
    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner', required=True)
    partner_address_id = fields.Many2one(
        string='Partner Address', comodel_name='res.partner', required=True)
    picking_ids = fields.Many2many(
        string='Pickings', comodel_name='stock.picking',
        relation='edicom_delivery_picking',
        column1='edicom_id', column2='picking_id')
    state = fields.Selection([
        ('notsent', 'Not sent'),
        ('sent', 'Sent'),
        ('resent', 'Re-Sent')
    ], string='Status', copy=False, default='notsent')

    _order = 'date'

    @api.model
    def _report_identifier_get(self, vals):
        company_id = vals.get('company_id', self.env.user.company_id.id)
        seq = self.env['ir.sequence'].search(
            [('name', '=', 'edicom_delivery_alert_sequence')],
            limit=1,
        )
        if not seq:
            raise exceptions.UserError(_(
                "Sequence not found"
            ))
        return seq.next_by_id()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self._report_identifier_get(vals)
        return super(EdicomDeliveryAlert, self).create(vals)

#     _sizes = [
#         ['NUMENT', 10], # secuencia
#         ['NUMENT2', 10], # secuencia
#         ['DES1', 25],
#         ['DES2', 6],
#         ['MDATE', 12], # Fecha mensaje
#         ['RDATE', 12], # Fecha entrega
#         ['DES3', 39],
#         ['NUMENT3', 10],
#     ]

    @api.multi
    def sent_edi(self):
        company = self.env.user.company_id
        path = company.edi_path
        out_char_sep = company.out_char_separator
        for alert in self:
            for picking in alert.picking_ids:
                file_suffix = str(alert.name)
                text = str(alert.name) + out_char_sep
                text += alert.date.strftime('%Y%m%d') + out_char_sep
                text += alert.date_sent.strftime('%Y%m%d%H%M') + out_char_sep
                text += alert.partner_address_id.codigo_edi or '' + out_char_sep
                text += alert.driver_plate or '' + out_char_sep
                text += alert.driver.codigo_edi or '' + out_char_sep
                text += alert.driver_vat or '' + out_char_sep
                text += alert.driver.name + out_char_sep
                text += alert.partner_id.codigo_edi or '' + out_char_sep
                if picking.sale_id:
                    sale = picking.sale_id.name
                else:
                    sale = ''
                text += sale + out_char_sep
                text += picking.name + out_char_sep
                text += '\r\n'
            print(text)
            print(path)
            outputFile = codecs.open(
                path + "/ALB_" + file_suffix + ".txt", "w", "iso-8859-1")
            outputFile.write(text)
            outputFile.close()
            if alert.state == 'notsent':
                alert.state = 'sent'
            else:
                alert.state = 'resent'
        return True
