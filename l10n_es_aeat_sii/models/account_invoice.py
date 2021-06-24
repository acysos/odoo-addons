# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Studio73 - Pablo Fuentes <pablo@studio73>
# Copyright 2017 Studio73 - Jordi Tolsà <jordi@studio73.es>
# Copyright 2018 Binovo IT Human Project SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from datetime import datetime, date
from requests import Session

from odoo import _, api, fields, exceptions, models
from odoo.exceptions import UserError, RedirectWarning, ValidationError

_logger = logging.getLogger(__name__)

try:
    from zeep import Client
    from zeep.transports import Transport
    from zeep.plugins import HistoryPlugin
except (ImportError, IOError) as err:
    _logger.debug(err)


try:
    from odoo.addons.queue_job.job import job
except ImportError:
    _logger.debug('Can not `import queue_job`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_default_sii_description(self):
        inv_type = self.env.context.get('type')
        if not inv_type:
            inv_type = self.env.context.get('inv_type')
        company = self.env.user.company_id
        method_desc = company.sii_description_method
        header_sale = company.sii_header_sale or ''
        header_purchase = company.sii_header_purchase or ''
        fixed_desc = company.sii_description or ''
        description = '/'
        if inv_type in ['out_invoice', 'out_refund'] and header_sale:
            description = header_sale
        if inv_type in ['in_invoice', 'in_refund'] and header_purchase:
            description = header_purchase
        if method_desc in ['fixed']:
            description += fixed_desc
        return description

    @api.multi
    @api.depends('invoice_line_ids')
    def _is_sii_mapped(self):
        for invoice in self:
            if invoice.company_id.sii_enabled:
                taxes = invoice._get_taxes_map(
                    ['SFESB', 'SFESISP', 'SFENS', 'SFESS', 'SFESBE', 'SFESBEI',
                     'SFESBEE', 'SFESSE', 'SFRS', 'SFRISP', 'SFRBI', 'RE',
                     'SFESNS'])
                invoice.is_sii_mapped = False
                for line in invoice.invoice_line_ids:
                    for tax_line in line.invoice_line_tax_ids:
                        if tax_line in taxes:
                            invoice.is_sii_mapped = True
            else:
                invoice.is_sii_mapped = False

    RECONCILE = [('1', 'No contrastable'),
                 ('2', 'En proceso de contraste'),
                 ('3', 'No contrastada'),
                 ('4', 'Parcialmente contrastada'),
                 ('5', 'Contrastada')]

    sii_description = fields.Text(
        string='SII Description', required=True,
        default=_get_default_sii_description)
    sii_sent = fields.Boolean(string='SII Sent', copy=False)
    sii_cancel = fields.Boolean(string='SII Cancel', copy=False, readonly=True)
    sii_csv = fields.Char(string='SII CSV', copy=False)
    sii_results = fields.One2many(
        comodel_name='aeat.sii.result', inverse_name='invoice_id',
        string='Invoice results', domain=[('inv_type', '=', 'normal')])
    sii_send_error = fields.Text(string='SII Send Error')
    sii_recc_sent = fields.Boolean(string='SII Payment RECC Sent', copy=False)
    sii_recc_csv = fields.Char(string='SII Payment RECC CSV', copy=False)
    sii_recc_results = fields.One2many(
        comodel_name='aeat.sii.result', inverse_name='invoice_id',
        string='Invoice results', domain=[('inv_type', '=', 'recc')])
    sii_recc_send_error = fields.Text(string='SII Payment RECC Send Error')
    refund_type = fields.Selection(
        selection=[('S', 'By substitution'), ('I', 'By differences')],
        string="Refund Type")
    sii_registration_date = fields.Date(
        string='SII registration date', readonly=True, copy=False)
    registration_key = fields.Many2one(
        comodel_name='aeat.sii.mapping.registration.keys',
        string="Registration key", required=False)
    sii_enabled = fields.Boolean(string='Enable SII',
                                 related='company_id.sii_enabled')
    invoice_jobs_ids = fields.Many2many(
        comodel_name='queue.job', column1='invoice_id', column2='job_id',
        string="Invoice Jobs", copy=False)
    is_sii_mapped = fields.Boolean(
        string='Is SII mapped', compute='_is_sii_mapped', store=True)
    sii_reconcile_state = fields.Selection(RECONCILE, string='Reconcile State',
                                           readonly=True, index=True)
    sii_check_results = fields.One2many(
        comodel_name='aeat.check.sii.result', inverse_name='invoice_id',
        string='Check results')
    sii_resend = fields.Boolean(
        string='SII Resend',
        help='Resend invoice. This is activate if some critical fields have'
            ' been changed')

    @api.onchange('refund_type')
    def onchange_refund_type(self):
        if self.refund_type == 'S' and not self.origin_invoice_ids:
            self.refund_type = False
            return {
                'warning': {'message': 'Debes tener al menos una factura '
                                       'vinculada que sustituir'}
            }

    @api.onchange('fiscal_position_id')
    def onchange_fiscal_position(self):
        for invoice in self:
            if invoice.fiscal_position_id and 'out' in invoice.type:
                invoice.registration_key = \
                    invoice.fiscal_position_id.sii_registration_key_sale
            elif invoice.fiscal_position_id:
                invoice.registration_key = \
                    invoice.fiscal_position_id.sii_registration_key_purchase

    @api.onchange('invoice_line_ids')
    def _get_sii_description_from_lines(self):
        for invoice in self:
            company = invoice.company_id
            method_desc = company.sii_description_method
            header_sale = company.sii_header_sale or ''
            header_purchase = company.sii_header_purchase or ''
            description = '/'
            if invoice.type in ['out_invoice', 'out_refund'] and header_sale:
                description = header_sale
            if invoice.type in ['in_invoice', 'in_refund'] and header_purchase:
                description = header_purchase
            if method_desc == 'auto':
                for line in invoice.invoice_line_ids:
                    description += line.name + ' - '
                invoice.sii_description = description

    @api.model
    def _get_tax_type(self, tax_line):
        if tax_line.amount_type == 'group':
            tax_type = abs(
                tax_line.children_tax_ids.filtered('amount')[:1].amount)
        else:
            tax_type = abs(tax_line.amount)
        return tax_type

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None,
            description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice, date, description,
            journal_id)
        values['refund_type'] = 'I'
        return values

    @api.model
    def create(self, vals):
        if not vals.get('fiscal_position_id', False):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            raise UserError(_(
                "No Fiscal Position configured for the partner %s") % (
                    partner.name))
        if vals.get('sii_enabled', False):
            vals.pop('sii_enabled')
        invoice = super(AccountInvoice, self).create(vals)
        if (vals.get('fiscal_position_id') and
                not vals.get('registration_key')):
            invoice.onchange_fiscal_position()
        if not vals.get('sii_description'):
            invoice._get_sii_description_from_lines()
        return invoice

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals:
            if self.sii_sent:
                raise UserError(_(
                    "This invoice is sent to SII, if you change the partner"
                    " you have to cancel it and drop the invoice from SII"))
            else:
                vals['sii_resend'] = True
        if ('number' in vals and self.type in ['out_invoice', 'out_refund']):
            if self.sii_sent and vals['number'] != self.number:
                raise UserError(_(
                    "This invoice is sent to SII, if you change the number"
                    " you have to cancel it and drop the invoice from SII"))
            elif vals['number'] != self.number:
                vals['sii_resend'] = True
        if ('reference' in vals and self.type in ['in_invoice', 'in_refund']):
            if self.sii_sent and vals['reference'] != self.reference:
                raise UserError(_(
                    "This invoice is sent to SII, if you change the number"
                    " you have to cancel it and drop the invoice from SII"))
            elif vals['reference'] != self.reference:
                vals['sii_resend'] = True
        if 'type' in vals:
            if self.sii_sent:
                raise UserError(_(
                    "This invoice is sent to SII, if you change the type"
                    " you have to cancel it and drop the invoice from SII"))
            else:
                vals['sii_resend'] = True
        if 'date_invoice' in vals:
            if self.sii_sent:
                raise UserError(_(
                    "This invoice is sent to SII, if you change the date"
                    " you have to cancel it and drop the invoice from SII"))
            else:
                vals['sii_resend'] = True
        if 'tax_line_ids' in vals or 'registation_key' in vals or \
                'refund_type' in vals:
            vals['sii_resend'] = True
        res = super(AccountInvoice, self).write(vals)
        if (vals.get('fiscal_position_id') and
                not vals.get('registration_key')):
            self.onchange_fiscal_position()
        if not vals.get('sii_description'):
            self._get_sii_description_from_lines()
        return res

    @api.multi
    def _get_sii_map(self):
        self.ensure_one()
        sii_map_obj = self.env['aeat.sii.map']
        sii_map_line_obj = self.env['aeat.sii.map.lines']
        sii_map = sii_map_obj.search(
            [('state', '=', False),
             '|',
             ('date_from', '<=', fields.Date.today()),
             ('date_from', '=', False),
             '|',
             ('date_to', '>=', fields.Date.today()),
             ('date_to', '=', False)], limit=1)
        if not sii_map:
            raise UserError(_(
                'SII Map not found. Check your configuration'))
        return sii_map

    @api.multi
    def map_tax_template(self, tax_template, mapping_taxes):
        # Adapted from account_chart_update module
        """Adds a tax template -> tax id to the mapping."""
        if not tax_template:
            return self.env['account.tax']
        if mapping_taxes.get(tax_template):
            return mapping_taxes[tax_template]
        # search inactive taxes too, to avoid re-creating
        # taxes that have been deactivated before
        tax_obj = self.env['account.tax'].with_context(active_test=False)
        criteria = ['|',
                    ('name', '=', tax_template.name),
                    ('description', '=', tax_template.name)]
        if tax_template.description:
            criteria = ['|', '|'] + criteria
            criteria += [('description', '=', tax_template.description),
                         ('name', '=', tax_template.description)]
        criteria += [('company_id', '=', self.company_id.id)]
        taxes = tax_obj.search(criteria)
        mapping_taxes[tax_template] = (
            taxes and taxes[0] or self.env['account.tax'])
        return mapping_taxes[tax_template]

    @api.multi
    def _get_taxes_map(self, codes):
        # Return the codes that correspond to that sii map line codes
        taxes = []
        sii_map_line_obj = self.env['aeat.sii.map.lines']
        sii_map = self._get_sii_map()
        mapping_taxes = {}
        for code in codes:
            tax_templates = sii_map_line_obj.search(
                [('code', '=', code), ('sii_map_id', '=', sii_map.id)],
                limit=1).taxes
            for tax_template in tax_templates:
                tax = self.map_tax_template(tax_template, mapping_taxes)
                if tax:
                    taxes.append(tax)
        return taxes

    @api.multi
    def _change_date_format(self, date):
        new_date = date.strftime('%d-%m-%Y')
        return new_date

    @api.multi
    def _get_vat_number(self, vat):
        if vat.startswith('ES'):
            nif = vat[2:]
        else:
            nif = vat
        return nif

    @api.multi
    def _get_header(self, tipo_comunicacion, sii_map):
        self.ensure_one()
        company = self.company_id
        if not company.vat:
            raise UserError(_(
                "No VAT configured for the company '{}'").format(company.name))
        id_version_sii = sii_map.version
        nif = self._get_vat_number(self.company_id.vat)
        header = {
            "IDVersionSii": id_version_sii,
            "Titular": {
                "NombreRazon": self.company_id.name[0:120],
                "NIF": nif}
        }
        header['TipoComunicacion'] = tipo_comunicacion
        return header

    @api.multi
    def _get_line_price_subtotal(self, line):
        self.ensure_one()
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        return price

    @api.multi
    def _get_tax_line_req(self, tax_type, line, line_taxes):
        self.ensure_one()
        taxes = False
        taxes_re = self._get_taxes_map(['RE'])
        if len(line_taxes) > 1:
            for tax in line_taxes:
                if tax in taxes_re:
                    price = self._get_line_price_subtotal(line)
                    taxes = tax.compute_all(
                        price_unit=price,
                        quantity=line.quantity, product=line.product_id,
                        partner=line.invoice_id.partner_id)
                    taxes['percentage'] = tax.amount
                    return taxes
        return taxes

    @api.multi
    def _get_sii_tax_line(self, tax_line, line, line_taxes):
        self.ensure_one()
        tax_type = self._get_tax_type(tax_line)
        tax_line_req = self._get_tax_line_req(tax_type, line, line_taxes)
        taxes = tax_line.compute_all(
            price_unit=self._get_line_price_subtotal(line),
            quantity=line.quantity, product=line.product_id,
            partner=line.invoice_id.partner_id)
        if self.type == 'out_refund' and self.refund_type == 'I':
            taxes_total = -taxes['total_excluded']
        else:
            taxes_total = taxes['total_excluded']
        taxes_amount = taxes['taxes'][0]['amount']
        if (self.currency_id !=
                self.company_id.currency_id):
            taxes_total = self.currency_id.with_context(
                    date=self._get_currency_rate_date()).compute(
                        taxes_total, self.company_id.currency_id)
            taxes_amount = self.currency_id.with_context(
                date=self._get_currency_rate_date()).compute(
                    taxes['taxes'][0]['amount'],
                    self.company_id.currency_id)
        tax_sii = {
            "TipoImpositivo": tax_type,
            "BaseImponible": taxes_total
        }
        if tax_line_req:
            tipo_recargo = tax_line_req['percentage']
            cuota_recargo = tax_line_req['taxes'][0]['amount']
            tax_sii['TipoRecargoEquivalencia'] = tipo_recargo
            tax_sii['CuotaRecargoEquivalencia'] = cuota_recargo
        if self.type in ['out_invoice', 'out_refund']:
            tax_sii['CuotaRepercutida'] = taxes_amount
        if self.type in ['in_invoice', 'in_refund']:
            tax_sii['CuotaSoportada'] = taxes_amount
        return tax_sii

    @api.multi
    def _update_sii_tax_line(self, tax_sii, tax_line, line, line_taxes):
        self.ensure_one()
        tax_type = self._get_tax_type(tax_line)
        tax_line_req = self._get_tax_line_req(tax_type, line, line_taxes)
        taxes = tax_line.compute_all(
            price_unit=self._get_line_price_subtotal(line),
            quantity=line.quantity, product=line.product_id,
            partner=line.invoice_id.partner_id)
        if tax_line_req:
            cuota_recargo = tax_line_req['taxes'][0]['amount']
            tax_sii[str(tax_type)]['CuotaRecargoEquivalencia'] += cuota_recargo

        if self.type == 'out_refund' and self.refund_type == 'I':
            taxes_total = -taxes['total_excluded']
        else:
            taxes_total = taxes['total_excluded']
        taxes_amount = taxes['taxes'][0]['amount']
        if (self.currency_id !=
                self.company_id.currency_id):
            taxes_total = self.currency_id.with_context(
                date=self._get_currency_rate_date()).compute(
                    taxes_total, self.company_id.currency_id)
            taxes_amount = self.currency_id.with_context(
                date=self._get_currency_rate_date()).compute(
                    taxes['taxes'][0]['amount'],
                    self.company_id.currency_id)
        tax_sii[str(tax_type)]['BaseImponible'] += taxes_total
        if self.type in ['out_invoice', 'out_refund']:
            tax_sii[str(tax_type)]['CuotaRepercutida'] += taxes_amount
        if self.type in ['in_invoice', 'in_refund']:
            tax_sii[str(tax_type)]['CuotaSoportada'] += taxes_amount
        return tax_sii

    @api.multi
    def _get_sii_out_taxes(self):
        self.ensure_one()
        taxes_sii = {}
        taxes_f = {}
        taxes_to = {}
        taxes_sfesb = self._get_taxes_map(['SFESB'])
        taxes_sfesbe = self._get_taxes_map(['SFESBE'])
        taxes_sfesbei = self._get_taxes_map(['SFESBEI'])
        taxes_sfesbee = self._get_taxes_map(['SFESBEE'])
        taxes_sfesisp = self._get_taxes_map(['SFESISP'])
        # taxes_sfesisps = self._get_taxes_map(['SFESISPS'], self.date_invoice)
        taxes_sfens = self._get_taxes_map(['SFENS'])
        taxes_sfess = self._get_taxes_map(['SFESS'])
        taxes_sfesse = self._get_taxes_map(['SFESSE'])
        taxes_sfesns = self._get_taxes_map(['SFESNS'])

        # Invoice with not subject lines with 'DesgloseTipoOperacon' 
        identifier = self._get_sii_identifier()
        ns_dt = False
        if 'IDOtro' in identifier and self.registration_key != '07':
            if identifier['IDOtro']['ID'][:3] != 'ESN':
                ns_dt = True

        for line in self.invoice_line_ids:
            for tax_line in line.invoice_line_tax_ids:
                if tax_line in taxes_sfesb or tax_line in taxes_sfesisp or \
                        tax_line in taxes_sfesbe or (
                            tax_line in taxes_sfens and not ns_dt):
                    if 'DesgloseFactura' not in taxes_sii:
                        taxes_sii['DesgloseFactura'] = {}
                    inv_breakdown = taxes_sii['DesgloseFactura']
                    if tax_line in taxes_sfesb or tax_line in taxes_sfesbe or \
                            tax_line in taxes_sfesbee or \
                            tax_line in taxes_sfesisp:
                        if 'Sujeta' not in inv_breakdown:
                            inv_breakdown['Sujeta'] = {}
                        # TODO l10n_es no tiene impuesto exento de bienes
                        # corrientes nacionales
                        if tax_line in taxes_sfesbe:
                            price_subtotal = line.price_subtotal
                            if (self.currency_id !=
                                    self.company_id.currency_id):
                                price_subtotal = self.currency_id.with_context(
                                    date=self._get_currency_rate_date(
                                        )).compute(price_subtotal,
                                                   self.company_id.currency_id)
                            if 'Exenta' not in inv_breakdown['Sujeta']:
                                inv_breakdown['Sujeta']['Exenta'] = {}
                                inv_breakdown['Sujeta']['Exenta'][
                                    'DetalleExenta'] = {
                                        'BaseImponible': price_subtotal}
                            else:
                                inv_breakdown['Sujeta']['Exenta'][
                                    'DetalleExenta'][
                                        'BaseImponible'] += price_subtotal

                        if tax_line in taxes_sfesb or \
                                tax_line in taxes_sfesisp:
                            if 'NoExenta' not in inv_breakdown[
                                    'Sujeta']:
                                inv_breakdown['Sujeta'][
                                    'NoExenta'] = {}
                            if tax_line in taxes_sfesisp:
                                tipo_no_exenta = 'S2'
                            else:
                                tipo_no_exenta = 'S1'
                            inv_breakdown['Sujeta']['NoExenta'][
                                'TipoNoExenta'] = tipo_no_exenta
                            if 'DesgloseIVA' not in inv_breakdown[
                                    'Sujeta']['NoExenta']:
                                inv_breakdown['Sujeta'][
                                    'NoExenta']['DesgloseIVA'] = {}
                                inv_breakdown['Sujeta'][
                                    'NoExenta']['DesgloseIVA'][
                                    'DetalleIVA'] = []
                            tax_type = self._get_tax_type(tax_line)
                            if str(tax_type) not in taxes_f:
                                taxes_f[str(tax_type)] = \
                                    self._get_sii_tax_line(
                                        tax_line, line,
                                        line.invoice_line_tax_ids)
                            else:
                                taxes_f = self._update_sii_tax_line(
                                    taxes_f, tax_line, line,
                                    line.invoice_line_tax_ids)

                    if tax_line in taxes_sfens and not ns_dt:
                        price_subtotal = line.price_subtotal
                        if (self.currency_id !=
                                self.company_id.currency_id):
                            price_subtotal = self.currency_id.with_context(
                                date=self._get_currency_rate_date(
                                    )).compute(price_subtotal,
                                               self.company_id.currency_id)
                        if 'NoSujeta' not in inv_breakdown:
                            inv_breakdown['NoSujeta'] = {}
                            if line.product_id.sii_not_subject_7_14:
                                if 'ImportePorArticulos7_14_Otros' not in \
                                        inv_breakdown['NoSujeta']:
                                    inv_breakdown['NoSujeta'] = {
                                        'ImportePorArticulos7_14_Otros': \
                                            price_subtotal}
                                else:
                                    inv_breakdown['NoSujeta'][
                                        'ImportePorArticulos7_14_Otros'] += \
                                            price_subtotal
                            else:
                                if 'ImporteTAIReglasLocalizacion' not in \
                                        inv_breakdown['NoSujeta']:
                                    inv_breakdown['NoSujeta'] = {
                                        'ImporteTAIReglasLocalizacion': price_subtotal
                                    }
                                else:
                                    inv_breakdown['NoSujeta'][
                                        'ImporteTAIReglasLocalizacion'] += \
                                            price_subtotal

                if tax_line in taxes_sfess or tax_line in taxes_sfesse or \
                    tax_line in taxes_sfesbee or tax_line in taxes_sfesbei or \
                        tax_line in taxes_sfesns or (
                            tax_line in taxes_sfens and ns_dt):
                    if 'DesgloseTipoOperacion' not in taxes_sii:
                        taxes_sii['DesgloseTipoOperacion'] = {}
                    type_breakdown = taxes_sii['DesgloseTipoOperacion']
                    if tax_line in taxes_sfess or \
                            tax_line in taxes_sfesse or \
                            tax_line in taxes_sfesns:
                        if 'PrestacionServicios' not in type_breakdown:
                            type_breakdown['PrestacionServicios'] = {}
                        op_key = 'PrestacionServicios'
                    if tax_line in taxes_sfesbee or tax_line in taxes_sfesbei \
                            or (tax_line in taxes_sfens and ns_dt):
                        if 'Entrega' not in type_breakdown:
                            type_breakdown['Entrega'] = {}
                        op_key = 'Entrega'
                    if tax_line in taxes_sfesns or (
                            tax_line in taxes_sfens and ns_dt):
                        price_subtotal = line.price_subtotal
                        if (self.currency_id !=
                                self.company_id.currency_id):
                            price_subtotal = self.currency_id.with_context(
                                date=self._get_currency_rate_date(
                                    )).compute(price_subtotal,
                                               self.company_id.currency_id)
                        if 'NoSujeta' not in type_breakdown[op_key]:
                            type_breakdown[op_key]['NoSujeta'] = {}
                            if line.product_id.sii_not_subject_7_14:
                                if 'ImportePorArticulos7_14_Otros' not in \
                                        type_breakdown[op_key]['NoSujeta']:
                                    type_breakdown[op_key]['NoSujeta'] = {
                                        'ImportePorArticulos7_14_Otros': \
                                            price_subtotal}
                                else:
                                    type_breakdown[op_key]['NoSujeta'][
                                        'ImportePorArticulos7_14_Otros'] += \
                                            price_subtotal
                            else:
                                if 'ImporteTAIReglasLocalizacion' not in \
                                        type_breakdown[op_key]['NoSujeta']:
                                    type_breakdown[op_key]['NoSujeta'] = {
                                        'ImporteTAIReglasLocalizacion': \
                                            price_subtotal
                                    }
                                else:
                                    type_breakdown[op_key]['NoSujeta'][
                                        'ImporteTAIReglasLocalizacion'] += \
                                            price_subtotal                                    
                    else:
                        if 'Sujeta' not in type_breakdown[op_key]:
                            type_breakdown[op_key]['Sujeta'] = {}
                    if tax_line in taxes_sfesse or \
                            tax_line in taxes_sfesbee or \
                            tax_line in taxes_sfesbei:
                        if self.type == 'out_refund' and self.refund_type == 'I':
                            price_subtotal = -line.price_subtotal
                        else:
                            price_subtotal = line.price_subtotal
                        if (self.currency_id !=
                                self.company_id.currency_id):
                            price_subtotal = self.currency_id.with_context(
                                date=self._get_currency_rate_date(
                                    )).compute(price_subtotal,
                                               self.company_id.currency_id)
                        if 'Exenta' not in type_breakdown[op_key]['Sujeta']:
                            type_breakdown[op_key]['Sujeta']['Exenta'] = {}
                            type_breakdown[op_key]['Sujeta']['Exenta'][
                                'DetalleExenta'] = {
                                    'BaseImponible': price_subtotal}
                            if tax_line in taxes_sfesbee:
                                type_breakdown[op_key]['Sujeta']['Exenta'][
                                    'DetalleExenta']['CausaExencion'] = 'E2'
                            if tax_line in taxes_sfesbei:
                                type_breakdown[op_key]['Sujeta']['Exenta'][
                                    'DetalleExenta']['CausaExencion'] = 'E5'
                        else:
                            type_breakdown[op_key]['Sujeta']['Exenta'][
                                'DetalleExenta'][
                                    'BaseImponible'] += price_subtotal
                    if tax_line in taxes_sfess:
                        if 'NoExenta' not in type_breakdown[
                                'PrestacionServicios']['Sujeta']:
                            type_breakdown['PrestacionServicios'][
                                'Sujeta']['NoExenta'] = {}
                            # TODO l10n_es_ no tiene impuesto ISP de servicios
                            # if tax_line in taxes_sfesisps:
                            #     TipoNoExenta = 'S2'
                            # else:
                            tipo_no_exenta = 'S1'
                            type_breakdown[
                                'PrestacionServicios']['Sujeta']['NoExenta'][
                                'TipoNoExenta'] = tipo_no_exenta
                        if 'DesgloseIVA' not in taxes_sii[
                            'DesgloseTipoOperacion']['PrestacionServicios'][
                                'Sujeta']['NoExenta']:
                            type_breakdown[
                                'PrestacionServicios']['Sujeta']['NoExenta'][
                                'DesgloseIVA'] = {}
                            type_breakdown[
                                'PrestacionServicios']['Sujeta']['NoExenta'][
                                'DesgloseIVA']['DetalleIVA'] = []
                        tax_type = self._get_tax_type(tax_line)
                        if str(tax_type) not in taxes_to:
                            taxes_to[str(tax_type)] = \
                                self._get_sii_tax_line(
                                    tax_line, line,
                                    line.invoice_line_tax_ids)
                        else:
                            taxes_to = self._update_sii_tax_line(
                                taxes_to, tax_line, line,
                                line.invoice_line_tax_ids)
        if len(taxes_f) > 0:
            for key, line in list(taxes_f.items()):
                if self.type == 'out_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaRepercutida', False):
                        line['CuotaRepercutida'] = \
                            -round(line['CuotaRepercutida'], 2)
                else:
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaRepercutida', False):
                        line['CuotaRepercutida'] = \
                            abs(round(line['CuotaRepercutida'], 2))
                line['BaseImponible'] = round(line['BaseImponible'], 2)
                if line.get('TipoImpositivo', False):
                    line['TipoImpositivo'] = round(line['TipoImpositivo'], 2)
                taxes_sii['DesgloseFactura']['Sujeta']['NoExenta'][
                    'DesgloseIVA']['DetalleIVA'].append(line)
        if len(taxes_to) > 0:
            for key, line in list(taxes_to.items()):
                if self.type == 'out_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaRepercutida', False):
                        line['CuotaRepercutida'] = \
                            -round(line['CuotaRepercutida'], 2)
                else:
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaRepercutida', False):
                        line['CuotaRepercutida'] = \
                            abs(round(line['CuotaRepercutida'], 2))
                line['BaseImponible'] = round(line['BaseImponible'], 2)
                taxes_sii['DesgloseTipoOperacion']['PrestacionServicios'][
                    'Sujeta']['NoExenta']['DesgloseIVA'][
                    'DetalleIVA'].append(line)
        if 'DesgloseFactura' in taxes_sii:
            t_key = 'DesgloseFactura'
            if 'NoSujeta' in taxes_sii[t_key]:
                if 'ImportePorArticulos7_14_Otros' in taxes_sii[t_key][
                        'NoSujeta']:
                    ns_key = 'ImportePorArticulos7_14_Otros'
                else:
                    ns_key = 'ImporteTAIReglasLocalizacion'
                taxes_sii[t_key]['NoSujeta'][ns_key] = round(
                    taxes_sii[t_key]['NoSujeta'][ns_key], 2)
                    
        if 'DesgloseTipoOperacion' in taxes_sii:
            t_key = 'DesgloseTipoOperacion'
            if 'Entrega' in taxes_sii[t_key] or \
                    'PrestacionServicios' in taxes_sii[t_key]:
                if 'Entrega' in taxes_sii[t_key]:
                    dt_key = 'Entrega'
                else:
                    dt_key = 'PrestacionServicios'
                if 'Sujeta' in taxes_sii[t_key][dt_key]:
                    if 'Exenta' in taxes_sii[t_key][
                            dt_key]['Sujeta']:
                        if 'DetalleExenta' in taxes_sii[t_key][dt_key][
                                'Sujeta']['Exenta']:
                            if 'BaseImponible' in taxes_sii[t_key][dt_key][
                                    'Sujeta']['Exenta']['DetalleExenta']:
                                taxes_sii[t_key][dt_key]['Sujeta']['Exenta'][
                                    'DetalleExenta']['BaseImponible'] = round(
                                        taxes_sii[t_key][dt_key]['Sujeta'][
                                            'Exenta']['DetalleExenta'][
                                                'BaseImponible'], 2
                                        )
                if 'NoSujeta' in taxes_sii[t_key][dt_key]:
                    if 'ImportePorArticulos7_14_Otros' in taxes_sii[t_key][
                            dt_key]['NoSujeta']:
                        ns_key = 'ImportePorArticulos7_14_Otros'
                    else:
                        ns_key = 'ImporteTAIReglasLocalizacion'
                    taxes_sii[t_key][dt_key]['NoSujeta'][ns_key] = round(
                        taxes_sii[t_key][dt_key]['NoSujeta'][ns_key], 2)
        if 'DesgloseTipoOperacion' in taxes_sii and \
                'DesgloseFactura' in taxes_sii:
            taxes_sii['DesgloseTipoOperacion']['Entrega'] = \
                taxes_sii['DesgloseFactura']
            del taxes_sii['DesgloseFactura']
        
        return taxes_sii

    @api.multi
    def _get_sii_in_taxes(self):
        self.ensure_one()
        taxes_sii = {}
        taxes_f = {}
        taxes_isp = {}
        taxes_sfrs = self._get_taxes_map(['SFRS'])
        taxes_sfrisp = self._get_taxes_map(['SFRISP'])
        for line in self.invoice_line_ids:
            for tax_line in line.invoice_line_tax_ids:
                if tax_line in taxes_sfrs or tax_line in taxes_sfrisp:
                    if tax_line in taxes_sfrisp:
                        if 'InversionSujetoPasivo' not in taxes_sii:
                            taxes_sii['InversionSujetoPasivo'] = {}
                            taxes_sii['InversionSujetoPasivo'][
                                'DetalleIVA'] = []
                        tax_type = self._get_tax_type(tax_line)
                        if str(tax_type) not in taxes_isp:
                            taxes_isp[str(tax_type)] = self._get_sii_tax_line(
                                tax_line, line, line.invoice_line_tax_ids)
                        else:
                            taxes_isp = self._update_sii_tax_line(
                                taxes_isp, tax_line, line,
                                line.invoice_line_tax_ids)
                    else:
                        if 'DesgloseIVA' not in taxes_sii:
                            taxes_sii['DesgloseIVA'] = {}
                            taxes_sii['DesgloseIVA'][
                                'DetalleIVA'] = []
                        tax_type = self._get_tax_type(tax_line)
                        if str(tax_type) not in taxes_f:
                            taxes_f[str(tax_type)] = self._get_sii_tax_line(
                                tax_line, line, line.invoice_line_tax_ids)
                        else:
                            taxes_f = self._update_sii_tax_line(
                                taxes_f, tax_line, line,
                                line.invoice_line_tax_ids)
        if len(taxes_f) > 0:
            for key, line in list(taxes_f.items()):
                if self.type == 'in_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaSoportada', False):
                        line['CuotaSoportada'] = \
                            -round(line['CuotaSoportada'], 2)
                    line['BaseImponible'] = -round(
                        line['BaseImponible'], 2)
                else:
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaSoportada', False):
                        line['CuotaSoportada'] = \
                            abs(round(line['CuotaSoportada'], 2))
                    line['BaseImponible'] = round(line['BaseImponible'], 2)
                if line.get('TipoImpositivo', False):
                    line['TipoImpositivo'] = round(line['TipoImpositivo'], 2)
                taxes_sii['DesgloseIVA']['DetalleIVA'].append(line)
        if len(taxes_isp) > 0:
            for key, line in list(taxes_isp.items()):
                if self.type == 'in_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaSoportada', False):
                        line['CuotaSoportada'] = \
                            -round(line['CuotaSoportada'], 2)
                    line['BaseImponible'] = -round(
                        line['BaseImponible'], 2)
                else:
                    if line.get('CuotaSoportada', False):
                        line['CuotaSoportada'] = \
                            round(line['CuotaSoportada'], 2)
                    line['BaseImponible'] = round(line['BaseImponible'], 2)
                if line.get('TipoImpositivo', False):
                    line['TipoImpositivo'] = round(line['TipoImpositivo'], 2)
                taxes_sii['InversionSujetoPasivo']['DetalleIVA'].append(line)
        return taxes_sii

    @api.multi
    def _get_tipo_factura(self):
        # TODO Los 5 tipos de facturas rectificativas
        self.ensure_one()
        tipo_factura = ''
        if self.type in ['out_invoice', 'in_invoice']:
            tipo_factura = 'F1'
        if self.type in ['out_refund', 'in_refund']:
            tipo_factura = 'R4'
        return tipo_factura

    @api.multi
    def _check_partner_vat(self):
        for invoice in self:
            if not invoice.partner_id.vat:
                raise UserError(
                    "The partner has not a VAT configured.")

    @api.multi
    def _get_not_amount_taxes(self):
        self.ensure_one()
        taxes_sfrs = self._get_taxes_map(['SFRS'])
        taxes_sfrisp = self._get_taxes_map(['SFRISP'])
        taxes_sfesb = self._get_taxes_map(['SFESB'])
        taxes_sfesbe = self._get_taxes_map(['SFESBE'])
        taxes_sfesbei = self._get_taxes_map(['SFESBEI'])
        taxes_sfesbee = self._get_taxes_map(['SFESBEE'])
        taxes_sfesisp = self._get_taxes_map(['SFESISP'])
        # taxes_sfesisps = self._get_taxes_map(['SFESISPS'], self.date_invoice)
        taxes_sfens = self._get_taxes_map(['SFENS'])
        taxes_sfess = self._get_taxes_map(['SFESS'])
        taxes_sfesse = self._get_taxes_map(['SFESSE'])
        taxes_sfesns = self._get_taxes_map(['SFESNS'])
        taxes_re = self._get_taxes_map(['RE'])
        all_taxes = taxes_sfrs + taxes_sfrisp + taxes_sfesb + taxes_sfesbe
        all_taxes += taxes_sfesbei + taxes_sfesbee + taxes_sfesisp
        all_taxes += taxes_sfens + taxes_sfess + taxes_sfesse + taxes_sfesns
        all_taxes += taxes_sfens + taxes_sfess + taxes_sfesse + taxes_sfesns + \
            taxes_re
        not_amount_taxes = 0.0
        for tax_line in self.tax_line_ids:
            if tax_line.tax_id not in all_taxes:
                not_amount_taxes += tax_line.amount
        return not_amount_taxes

    @api.multi
    def _get_invoices(self):
        self.ensure_one()
        sii_map = self._get_sii_map()
        self._check_partner_vat()
        invoice_date = self._change_date_format(self.date_invoice)
        company = self.company_id
        ejercicio = fields.Date.from_string(
            self.date).year
        periodo = '%02d' % fields.Date.from_string(
            self.date).month
        if not company.chart_template_id:
            raise UserError(_(
                'You have to select what account chart template use this'
                ' company.'))
        if not self.registration_key:
            raise UserError(_(
                'You have to select a registration key in SII Tab.'))
        key = self.registration_key.code
        tipo_factura = self._get_tipo_factura()
        if self.partner_id.is_company:
            nombrerazon = self.partner_id.name[0:120]
        else:
            if self.partner_id.parent_id:
                nombrerazon = self.partner_id.parent_id.name[0:120]
            else:
                nombrerazon = self.partner_id.name[0:120]
        if self.type in ['out_invoice', 'out_refund']:
            tipo_desglose = self._get_sii_out_taxes()
            not_amount_taxes = self._get_not_amount_taxes()
            importe_total = self.amount_total - not_amount_taxes
            if self.type == 'out_refund' and self.refund_type == 'I':
                importe_total = -abs(importe_total)
            if (self.currency_id !=
                    self.company_id.currency_id):
                importe_total = round(
                    self.currency_id.with_context(
                        date=self._get_currency_rate_date(
                            )).compute(importe_total,
                                    self.company_id.currency_id),
                    2)
            nif = self._get_vat_number(company.vat)
            invoices = {
                "IDFactura": {
                    "IDEmisorFactura": {
                        "NIF": nif
                    },
                    "NumSerieFacturaEmisor": self.number[0:60],
                    "FechaExpedicionFacturaEmisor": invoice_date},
                "FacturaExpedida": {
                    "TipoFactura": tipo_factura,
                    "ClaveRegimenEspecialOTrascendencia": key,
                    "DescripcionOperacion": self.sii_description[0:500],
                    "Contraparte": {
                        "NombreRazon": nombrerazon
                    },
                    "TipoDesglose": tipo_desglose,
                    "ImporteTotal": importe_total
                }
            }
            if sii_map.version == '1.0':
                invoices['PeriodoImpositivo'] = {
                    "Ejercicio": ejercicio,
                    "Periodo": periodo
                }
            else:
                invoices['PeriodoLiquidacion'] = {
                    "Ejercicio": ejercicio,
                    "Periodo": periodo
                }
                if self.amount_total >= 100000000:
                    invoices['FacturaExpedida']['Macrodato'] = 'S'
            # Uso condicional de IDOtro/NIF
            invoices['FacturaExpedida']['Contraparte'].update(
                self._get_sii_identifier())
            if self.type == 'out_refund':
                invoices['FacturaExpedida'][
                    'TipoRectificativa'] = self.refund_type

                if self.refund_type == 'S':
                    base_rectificada = 0
                    cuota_rectificada = 0
                    for s in self.origin_invoices_ids:
                        base_rectificada += s.amount_untaxed
                        cuota_rectificada += s.amount_tax
                    invoices['FacturaExpedida']['ImporteRectificacion'] = {
                        'BaseRectificada': base_rectificada,
                        'CuotaRectificada': cuota_rectificada
                    }

            if ('IDOtro' in invoices['FacturaExpedida']['Contraparte'] or
                ('NIF' in invoices['FacturaExpedida']['Contraparte'] and
                 invoices['FacturaExpedida']['Contraparte']['NIF'].startswith(
                    'N') and self.partner_id.country_id.code == 'ES')):
                if 'DesgloseFactura' in invoices[
                        'FacturaExpedida']['TipoDesglose']:
                    if 'DesgloseTipoOperacion' not in invoices[
                            'FacturaExpedida']['TipoDesglose']:
                        invoices['FacturaExpedida']['TipoDesglose'][
                            'DesgloseTipoOperacion'] = {}
                    invoices['FacturaExpedida']['TipoDesglose'][
                        'DesgloseTipoOperacion']['Entrega'] = invoices[
                            'FacturaExpedida']['TipoDesglose'][
                                'DesgloseFactura']
                    invoices['FacturaExpedida']['TipoDesglose'].pop(
                        'DesgloseFactura')

        if self.type in ['in_invoice', 'in_refund']:
            desglose_factura = self._get_sii_in_taxes()
            cuota_deducible = 0
            if 'DesgloseIVA' in desglose_factura:
                for desglose in desglose_factura['DesgloseIVA']['DetalleIVA']:
                    cuota_deducible += desglose['CuotaSoportada']
            reg_date = self._change_date_format(
                self.sii_registration_date or fields.Date.today())
            not_amount_taxes = self._get_not_amount_taxes()
            importe_total = self.amount_total - not_amount_taxes
            if self.type == 'in_refund' and self.refund_type == 'I':
                importe_total = -abs(importe_total)
            if (self.currency_id !=
                    self.company_id.currency_id):
                importe_total = self.currency_id.with_context(
                    date=self._get_currency_rate_date()).compute(
                        importe_total, self.company_id.currency_id)
            if not self.reference:
                raise UserError(_(
                    'The invoice supplier number is required'))
            invoices = {
                "IDFactura": {
                    "IDEmisorFactura": {},
                    "NumSerieFacturaEmisor":
                    self.reference and
                    self.reference[0:60],
                    "FechaExpedicionFacturaEmisor": invoice_date},
                "FacturaRecibida": {
                    "TipoFactura": tipo_factura,
                    "ClaveRegimenEspecialOTrascendencia": key,
                    "DescripcionOperacion": self.sii_description[0:500],
                    "DesgloseFactura": desglose_factura,
                    "Contraparte": {
                        "NombreRazon": nombrerazon
                    },
                    "FechaRegContable": reg_date,
                    "CuotaDeducible": round(cuota_deducible, 2),
                    "ImporteTotal": round(importe_total, 2)
                }
            }
            if sii_map.version == '1.0':
                invoices['PeriodoImpositivo'] = {
                    "Ejercicio": ejercicio,
                    "Periodo": periodo
                }
            else:
                invoices['PeriodoLiquidacion'] = {
                    "Ejercicio": ejercicio,
                    "Periodo": periodo
                }
                if self.amount_total >= 100000000:
                    invoices['FacturaExpedida']['Macrodato'] = 'S'
            id_emisor = self._get_sii_identifier()
            invoices['IDFactura']['IDEmisorFactura'].update(id_emisor)
            invoices['FacturaRecibida']['Contraparte'].update(id_emisor)
            if self.type == 'in_refund':
                invoices['FacturaRecibida'][
                    'TipoRectificativa'] = self.refund_type

                if self.refund_type == 'S':
                    base_rectificada = 0
                    cuota_rectificada = 0
                    for s in self.origin_invoice_ids:
                        base_rectificada += s.amount_untaxed
                        cuota_rectificada += s.amount_tax
                    invoices['FacturaRecibida']['ImporteRectificacion'] = {
                        'BaseRectificada': base_rectificada,
                        'CuotaRectificada': cuota_rectificada
                    }
        return invoices

    @api.multi
    def _connect_sii(self, wsdl):
        today = fields.Date.today()
        sii_config = self.env['l10n.es.aeat.sii'].search([
            ('company_id', '=', self.company_id.id),
            ('public_key', '!=', False),
            ('private_key', '!=', False),
            '|', ('date_start', '=', False),
            ('date_start', '<=', today),
            '|', ('date_end', '=', False),
            ('date_end', '>=', today),
            ('state', '=', 'active')
        ], limit=1)
        if sii_config:
            public_crt = sii_config.public_key
            private_key = sii_config.private_key
        else:
            public_crt = self.env['ir.config_parameter'].get_param(
                'l10n_es_aeat_sii.publicCrt', False)
            private_key = self.env['ir.config_parameter'].get_param(
                'l10n_es_aeat_sii.privateKey', False)

        session = Session()
        session.cert = (public_crt, private_key)
        transport = Transport(session=session)

        history = HistoryPlugin()
        client = Client(wsdl=wsdl, transport=transport, plugins=[history])
        return client

    @api.multi
    def _get_test_mode(self, port_name):
        self.ensure_one()
        if self.company_id.sii_test:
            port_name += 'Pruebas'
        return port_name

    @api.multi
    def _connect_wsdl(self, wsdl, port_name):
        self.ensure_one()
        client = self._connect_sii(wsdl)
        port_name = self._get_test_mode(port_name)
        serv = client.bind('siiService', port_name)
        return serv

    @api.multi
    def _send_soap(self, wsdl, port_name, operation, param1, param2):
        self.ensure_one()
        serv = self._connect_wsdl(wsdl, port_name)
        res = serv[operation](param1, param2)
        return res

    @api.multi
    def _create_fail_activity(self):
        self.ensure_one()
        if self.company_id.sii_activity_type:
            model_id = self.env['ir.model'].search(
                [('model', '=', 'account.invoice')])
            company = self.company_id
            user_id = self.user_id.id
            if company.sii_activity_user:
                user_id = company.sii_activity_user.id
            date_deadline = fields.Date.today().strftime('%Y-%m-%d')
            activity_vals = {
                'activity_type_id': company.sii_activity_type.id,
                'res_id': self.id,
                'res_model_id': model_id[0].id,
                'date_deadline': date_deadline,
                'user_id': user_id,
                'summary': 'SII Error: ' + self.number,
            }
            self.env['mail.activity'].create(activity_vals)

    @api.multi
    def _send_invoice_to_sii(self):
        for invoice in self.filtered(
                lambda i: i.state in ['open', 'paid'] and i.is_sii_mapped and (
                    not i.sii_sent or (i.sii_sent and i.sii_resend))):
            sii_map = invoice._get_sii_map()
            if invoice.type in ['out_invoice', 'out_refund']:
                wsdl = sii_map._get_wsdl('wsdl_out')
                port_name = 'SuministroFactEmitidas'
                operation = 'SuministroLRFacturasEmitidas'
            elif self.type in ['in_invoice', 'in_refund']:
                wsdl = sii_map._get_wsdl('wsdl_in')
                port_name = 'SuministroFactRecibidas'
                operation = 'SuministroLRFacturasRecibidas'
            if not invoice.sii_sent:
                tipo_comunicacion = 'A0'
            else:
                tipo_comunicacion = 'A1'
            header = invoice._get_header(tipo_comunicacion, sii_map)
            invoices = invoice._get_invoices()

            try:
                res = invoice._send_soap(
                    wsdl, port_name, operation, header, invoices)
                # TODO Facturas intracomunitarias 66 RIVA
                # elif invoice.fiscal_position.id == self.env.ref(
                #     'account.fp_intra').id:
                #     res = serv.SuministroLRDetOperacionIntracomunitaria(
                #         header, invoices)
                if res['EstadoEnvio'] in ['Correcto', 'ParcialmenteCorrecto']:
                    self.sii_sent = True
                    self.sii_resend = False
                    self.sii_cancel = False
                    self.sii_csv = res['CSV']
                    if 'FechaRegContable' in invoices:
                        if not self.sii_registration_date:
                            self.sii_registration_date = \
                                self._change_date_format(fields.Date.today())
                else:
                    self.sii_sent = False
                    self.sii_resend = False
                    self._create_fail_activity()
                self.env['aeat.sii.result'].sudo().create_result(
                    invoice, res, 'normal', False, 'account.invoice')
                send_error = False
                res_line = res['RespuestaLinea'][0]
                if res_line['CodigoErrorRegistro']:
                    send_error = "{} | {}".format(
                        str(res_line['CodigoErrorRegistro']),
                        str(res_line['DescripcionErrorRegistro'])[:60])
                self.sii_send_error = send_error
            except Exception as fault:
                self.env['aeat.sii.result'].sudo().sudo().create_result(
                    invoice, False, 'normal', fault, 'account.invoice')
                self.sii_send_error = fault
                self._create_fail_activity()

    @api.multi
    def send_recc_payment_registry(self, move):
        for invoice in self:
            sii_map = invoice._get_sii_map()
            if invoice.type in ['out_invoice', 'out_refund']:
                wsdl = sii_map._get_wsdl('wsdl_pr')
                port_name = 'SuministroCobrosEmitidas'
                operation = 'SuministroLRCobrosEmitidas'
                importe = move.debit
            elif invoice.type in ['in_invoice', 'in_refund']:
                wsdl = sii_map._get_wsdl('wsdl_ps')
                port_name = 'SuministroPagosRecibidas'
                operation = 'SuministroLRPagosRecibidas'
                importe = move.credit
            header = invoice._get_header(False, sii_map)
            fecha = self._change_date_format(move.reconcile_id.create_date)
            pay = {
                'Fecha': fecha,
                'Importe': importe,
                'Medio': invoice.payment_mode_id.sii_key.code,
            }
            try:
                invoice_date = self._change_date_format(invoice.date_invoice)
                if invoice.type in ['out_invoice', 'out_refund']:
                    nif = self._get_vat_number(invoice.company_id.vat)
                    payment = {
                        "IDFactura": {
                            "IDEmisorFactura": {
                                "NIF": nif
                            },
                            "NumSerieFacturaEmisor": invoice.number[0:60],
                            "FechaExpedicionFacturaEmisor": invoice_date},
                    }
                    payment['Cobros'] = {}
                    payment['Cobros']['Cobro'] = []
                    payment['Cobros']['Cobro'].append(pay)
                elif invoice.type in ['in_invoice', 'in_refund']:
                    payment = {
                        "IDFactura": {
                            "IDEmisorFactura": {
                                "NombreRazon": invoice.partner_id.name[0:120]
                            },
                            "NumSerieFacturaEmisor":
                            invoice.supplier_invoice_number and
                            invoice.supplier_invoice_number[0:60],
                            "FechaExpedicionFacturaEmisor": invoice_date},
                    }
                    id_emisor = invoice._get_sii_identifier()
                    payment['IDFactura']['IDEmisorFactura'].update(id_emisor)
                    payment['Pagos'] = {}
                    payment['Pagos']['Pago'] = []
                    payment['Pagos']['Pago'].append(pay)
                res = invoice._send_soap(
                    wsdl, port_name, operation, header, payment)
                if res['EstadoEnvio'] in ['Correcto', 'AceptadoConErrores']:
                    invoice.sii_recc_sent = True
                    invoice.sii_recc_csv = res['CSV']
                else:
                    invoice.sii_recc_sent = False
                self.env['aeat.sii.result'].sudo().create_result(
                    invoice, res, 'recc', False, 'account.invoice')
                send_recc_error = False
                res_line = res['RespuestaLinea'][0]
                if res_line['CodigoErrorRegistro']:
                    send_recc_error = "{} | {}".format(
                        str(res_line['CodigoErrorRegistro']),
                        str(res_line['DescripcionErrorRegistro'])[:60])
                invoice.sii_recc_send_error = send_recc_error
            except Exception as fault:
                self.env['aeat.sii.result'].sudo().create_result(
                    invoice, False, 'recc', fault, 'account.invoice')
                invoice.sii_recc_send_error = fault

    @api.multi
    def send_recc_payment(self, move):
        queue_obj = self.env['queue.job'].sudo()
        for invoice in self:
            company = invoice.company_id
            if company.sii_enabled and company.sii_method == 'auto' and \
                    invoice.is_sii_invoice():
                if not company.use_connector:
                    invoice.send_recc_payment_registry(move)
                else:
                    eta = company._get_sii_eta()
                    new_delay = self.sudo().with_context(
                        company_id=company.id
                    ).with_delay(eta=eta).send_recc_payment_job(move)
                    job = queue_obj.search([
                        ('uuid', '=', new_delay.uuid)
                    ], limit=1)
                    move.invoice.invoice_jobs_ids |= job

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        queue_obj = self.env['queue.job'].sudo()
        for invoice in self:
            company = invoice.company_id
            if company.sii_enabled and company.sii_method == 'auto' and \
                    invoice.is_sii_invoice():
                if not company.use_connector:
                    invoice._send_invoice_to_sii()
                else:
                    eta = company._get_sii_eta()
                    new_delay = self.sudo().with_context(
                        company_id=company.id
                    ).with_delay(eta=eta).confirm_one_invoice()
                    job = queue_obj.search([
                        ('uuid', '=', new_delay.uuid)
                    ], limit=1)
                    invoice.sudo().invoice_jobs_ids |= job
        return res

    @api.multi
    def send_sii(self):
        queue_obj = self.env['queue.job'].sudo()
        for invoice in self:
            if invoice.sii_sent:
                invoice.sii_resend = True
            company = invoice.company_id
            if company.sii_enabled and invoice.is_sii_invoice():
                if not company.use_connector:
                    invoice._send_invoice_to_sii()
                else:
                    eta = company._get_sii_eta()
                    new_delay = invoice.sudo().with_context(
                        company_id=company.id
                    ).with_delay(eta=eta).confirm_one_invoice()
                    job = queue_obj.search([
                        ('uuid', '=', new_delay.uuid)
                    ], limit=1)
                    invoice.sudo().invoice_jobs_ids |= job

    @api.multi
    def action_cancel(self):
        for queue in self.invoice_jobs_ids:
            if queue.state == 'started':
                raise UserError(_(
                    'You can not cancel this invoice because'
                    ' there is a job running!'))
            elif queue.state in ('pending', 'enqueued', 'failed'):
                queue.write({
                    'state': 'done',
                    'date_done': date.today()})
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def _fix_country_code(self, dic_ret):
        if dic_ret['IDOtro']['CodigoPais'] == 'UK':
            dic_ret['IDOtro']['CodigoPais'] = 'GB'
        if dic_ret['IDOtro']['CodigoPais'] == 'RE':
            dic_ret['IDOtro']['CodigoPais'] = 'FR'
        if dic_ret['IDOtro']['CodigoPais'] == 'GP':
            dic_ret['IDOtro']['CodigoPais'] = 'FR'
        if dic_ret['IDOtro']['CodigoPais'] == 'MQ':
            dic_ret['IDOtro']['CodigoPais'] = 'FR'
        if dic_ret['IDOtro']['CodigoPais'] == 'GF':
            dic_ret['IDOtro']['CodigoPais'] = 'FR'
        return dic_ret

    @api.multi
    def _get_sii_identifier(self):
        self.ensure_one()
        dic_ret = {}
        vat = ''.join(e for e in self.partner_id.vat if e.isalnum()).upper()
        nif = self._get_vat_number(vat)
        if self.fiscal_position_id.name == 'Régimen Intracomunitario':
            dic_ret = {
                "IDOtro": {
                    "CodigoPais":
                        self.partner_id.country_id and
                        self.partner_id.country_id.code or
                        vat[:2],
                    "IDType": '02',
                    "ID": nif
                }
            }
            dic_ret = self._fix_country_code(dic_ret)
        elif self.fiscal_position_id.name == \
                'Régimen Extracomunitario' or self.fiscal_position_id.name == \
                    'Régimen Extracomunitario / Canarias, Ceuta y Melilla':
            dic_ret = {
                "IDOtro": {
                    "CodigoPais":
                        self.partner_id.country_id and
                        self.partner_id.country_id.code or
                        vat[:2],
                    "IDType": '04',
                    "ID": nif
                  }
            }
            dic_ret = self._fix_country_code(dic_ret)
        elif self.partner_id.country_id.code == 'ES':
            dic_ret = {"NIF": nif}
        else:
            dic_ret = {
                "IDOtro": {
                    "CodigoPais":
                        self.partner_id.country_id and
                        self.partner_id.country_id.code or
                        vat[:2],
                    "IDType": '04',
                    "ID": nif
                  }
            }
        return dic_ret

    def is_sii_invoice(self):
        """ is_sii_invoice() -> bool
            Hook method to be overridden in additional modules to verify
            if the invoice must be sended trought SII system, for
            special cases.
            :param
            :return: bool
        """
        return True

    @api.multi
    def drop_sii(self):
        queue_obj = self.env['queue.job'].sudo()
        for invoice in self:
            company = invoice.company_id
            if company.sii_enabled:
                if not company.use_connector:
                    invoice._drop_invoice()
                else:
                    eta = company._get_sii_eta()
                    new_delay = self.sudo().with_context(
                        company_id=company.id
                    ).with_delay(eta=eta).drop_one_invoice()
                    job = queue_obj.search([
                        ('uuid', '=', new_delay.uuid)
                    ], limit=1)
                    invoice.sudo().invoice_jobs_ids |= job

    @api.multi
    def _drop_invoice(self):
        """ Drop invoice from SII"""
        queue_obj = self.env['queue.job'].sudo()
        for invoice in self.filtered(lambda i: i.state in ['cancel']):
            sii_map = invoice._get_sii_map()
            company = invoice.company_id
            nif = self._get_vat_number(company.vat)
            if invoice.type in ['out_invoice', 'out_refund']:
                wsdl = sii_map._get_wsdl('wsdl_out')
                port_name = 'SuministroFactEmitidas'
                operation = 'AnulacionLRFacturasEmitidas'
                number = invoice.number[0:60]
                id_emisor = {"NIF": nif}
            elif self.type in ['in_invoice', 'in_refund']:
                wsdl = sii_map._get_wsdl('wsdl_in')
                port_name = 'SuministroFactRecibidas'
                operation = 'AnulacionLRFacturasRecibidas'
                number = invoice.reference and \
                    invoice.reference[0:60]
                id_emisor = self._get_sii_identifier()
                id_emisor['NombreRazon'] = self.partner_id.name
            header = invoice._get_header(False, sii_map)
            ejercicio = fields.Date.from_string(
                self.date).year
            periodo = '%02d' % fields.Date.from_string(
                self.date).month
            invoice_date = self._change_date_format(invoice.date_invoice)
            try:
                query = {
                    "PeriodoLiquidacion": {
                        "Ejercicio": ejercicio,
                        "Periodo": periodo
                    },
                    "IDFactura": {
                        "IDEmisorFactura": id_emisor,
                        "NumSerieFacturaEmisor": number,
                        "FechaExpedicionFacturaEmisor": invoice_date
                    }
                }
                res = invoice._send_soap(
                    wsdl, port_name, operation, header, query)
                self.env['aeat.sii.result'].sudo().create_result(
                    invoice, res, 'normal', False, 'account.invoice')
                if res['EstadoEnvio'] in ['Correcto', 'ParcialmenteCorrecto']:
                    self.sii_sent = False
                    self.sii_cancel = True
                    self.sii_csv = res['CSV']
                else:
                    self.sii_sent = True
            except Exception as fault:
                self.env['aeat.sii.result'].sudo().create_result(
                    invoice, False, 'normal', fault, 'account.invoice')

    @api.multi
    def check_sii(self):
        queue_obj = self.env['queue.job'].sudo()
        for invoice in self:
            company = invoice.company_id
            if company.sii_enabled:
                if not company.use_connector:
                    invoice._check_invoice()
                else:
                    eta = company._get_sii_eta()
                    new_delay = self.sudo().with_context(
                        company_id=company.id
                    ).with_delay(eta=eta).check_one_invoice()
                    job = queue_obj.search([
                        ('uuid', '=', new_delay.uuid)
                    ], limit=1)
                    invoice.sudo().invoice_jobs_ids |= job

    @api.multi
    def _check_invoice(self):
        """ Request information to AEAT """
        for invoice in self.filtered(lambda i: i.state in ['open', 'paid']):
            sii_map = invoice._get_sii_map()
            if invoice.type in ['out_invoice', 'out_refund']:
                wsdl = sii_map._get_wsdl('wsdl_out')
                port_name = 'SuministroFactEmitidas'
                operation = 'ConsultaLRFacturasEmitidas'
                number = invoice.number[0:60]
            elif self.type in ['in_invoice', 'in_refund']:
                wsdl = sii_map._get_wsdl('wsdl_in')
                port_name = 'SuministroFactRecibidas'
                operation = 'ConsultaLRFacturasRecibidas'
                number = invoice.reference and \
                    invoice.reference[0:60]
            header = invoice._get_header(False, sii_map)
            ejercicio = fields.Date.from_string(
                self.date).year
            periodo = '%02d' % fields.Date.from_string(
                self.date).month
            invoice_date = self._change_date_format(invoice.date_invoice)
            try:
                query = {
                    "IDFactura": {
                        "NumSerieFacturaEmisor": number,
                        "FechaExpedicionFacturaEmisor": invoice_date
                    }
                }
                if sii_map.version == '1.0':
                    query['PeriodoImpositivo'] = {
                        "Ejercicio": ejercicio,
                        "Periodo": periodo
                    }
                else:
                    query['PeriodoLiquidacion'] = {
                        "Ejercicio": ejercicio,
                        "Periodo": periodo
                    }
                res = invoice._send_soap(
                    wsdl, port_name, operation, header, query)
                self.env['aeat.check.sii.result'].sudo().create_result(
                    invoice, res, False, 'account.invoice')
            except Exception as fault:
                self.env['aeat.check.sii.result'].sudo().create_result(
                    invoice, False, fault, 'account.invoice')

    @job
    @api.multi
    def confirm_one_invoice(self):
        self._send_invoice_to_sii()

    @job
    @api.multi
    def check_one_invoice(self):
        self._check_invoice()

    @job
    @api.multi
    def drop_one_invoice(self):
        self._drop_invoice()

    @job
    @api.multi
    def send_recc_payment_job(self, move):
        if move.exists() and move.invoice:
            move.invoice.send_recc_payment_registry(move)
