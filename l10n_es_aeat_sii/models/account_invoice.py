# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2017 Studio73 - Pablo Fuentes <pablo@studio73>
# Copyright 2017 Studio73 - Jordi Tolsà <jordi@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from datetime import datetime, date
from requests import Session

from odoo import _, api, fields, exceptions, models
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.modules.registry import Registry

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
            taxes = invoice._get_taxes_map(
                ['SFESB', 'SFESISP', 'SFENS', 'SFESS', 'SFESBE', 'SFESBEI',
                 'SFESBEE', 'SFESSE', 'SFRS', 'SFRISP', 'SFRBI', 'RE'])
            invoice.is_sii_mapped = False
            for line in invoice.invoice_line_ids:
                for tax_line in line.invoice_line_tax_ids:
                    if tax_line in taxes:
                        invoice.is_sii_mapped = True

    RECONCILE = [('1', 'No contrastable'),
                 ('2', 'En proceso de contraste'),
                 ('3', 'No contrastada'),
                 ('4', 'Parcialmente contrastada'),
                 ('5', 'Contrastada')]

    sii_description = fields.Text(
        string='SII Description', required=True,
        default=_get_default_sii_description)
    sii_sent = fields.Boolean(string='SII Sent', copy=False)
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
            raise exceptions.Warning(_(
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
        datetimeobject = datetime.strptime(date, '%Y-%m-%d')
        new_date = datetimeobject.strftime('%d-%m-%Y')
        return new_date

    @api.multi
    def _get_header(self, tipo_comunicacion, sii_map):
        self.ensure_one()
        company = self.company_id
        if not company.vat:
            raise UserError(_(
                "No VAT configured for the company '{}'").format(company.name))
        id_version_sii = sii_map.version
        header = {
            "IDVersionSii": id_version_sii,
            "Titular": {
                "NombreRazon": self.company_id.name[0:120],
                "NIF": self.company_id.vat[2:]}
        }
        if tipo_comunicacion:
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
        if tax_line.amount_type == 'group':
            tax_type = abs(
                tax_line.children_tax_ids.filtered('amount')[:1].amount)
        else:
            tax_type = abs(tax_line.amount)
        tax_line_req = self._get_tax_line_req(tax_type, line, line_taxes)
        taxes = tax_line.compute_all(
            price_unit=self._get_line_price_subtotal(line),
            quantity=line.quantity, product=line.product_id,
            partner=line.invoice_id.partner_id)
        tax_sii = {
            "TipoImpositivo": tax_type,
            "BaseImponible": taxes['total_excluded']
        }
        if tax_line_req:
            tipo_recargo = tax_line_req['percentage']
            cuota_recargo = tax_line_req['taxes'][0]['amount']
            tax_sii['TipoRecargoEquivalencia'] = tipo_recargo
            tax_sii['CuotaRecargoEquivalencia'] = cuota_recargo

        if self.type in ['out_invoice', 'out_refund']:
            tax_sii['CuotaRepercutida'] = taxes['taxes'][0]['amount']
        if self.type in ['in_invoice', 'in_refund']:
            tax_sii['CuotaSoportada'] = taxes['taxes'][0]['amount']
        return tax_sii

    @api.multi
    def _update_sii_tax_line(self, tax_sii, tax_line, line, line_taxes):
        self.ensure_one()
        tax_type = tax_line.amount * 100
        tax_line_req = self._get_tax_line_req(tax_type, line, line_taxes)
        taxes = tax_line.compute_all(
            price_unit=self._get_line_price_subtotal(line),
            quantity=line.quantity, product=line.product_id,
            partner=line.invoice_id.partner_id)
        if tax_line_req:
            cuota_recargo = tax_line_req['taxes'][0]['amount']
            tax_sii[str(tax_type)]['CuotaRecargoEquivalencia'] += cuota_recargo

        tax_sii[str(tax_type)]['BaseImponible'] += taxes['total_excluded']
        if self.type in ['out_invoice', 'out_refund']:
            tax_sii[str(tax_type)]['CuotaRepercutida'] += \
                taxes['taxes'][0]['amount']
        if self.type in ['in_invoice', 'in_refund']:
            tax_sii[str(tax_type)]['CuotaSoportada'] += \
                taxes['taxes'][0]['amount']
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

        for line in self.invoice_line_ids:
            for tax_line in line.invoice_line_tax_ids:
                if tax_line in taxes_sfesb or tax_line in taxes_sfesisp or \
                        tax_line in taxes_sfens or tax_line in taxes_sfesbe:
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
                            if 'Exenta' not in inv_breakdown['Sujeta']:
                                inv_breakdown['Sujeta']['Exenta'] = {}
                                inv_breakdown['Sujeta']['Exenta'][
                                    'DetalleExenta'] = {
                                        'BaseImponible': line.price_subtotal}
                            else:
                                inv_breakdown['Sujeta']['Exenta'][
                                    'DetalleExenta'][
                                        'BaseImponible'] += line.price_subtotal

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
                            tax_type = tax_line.amount * 100
                            if str(tax_type) not in taxes_f:
                                taxes_f[str(tax_type)] = \
                                    self._get_sii_tax_line(
                                        tax_line, line,
                                        line.invoice_line_tax_ids)
                            else:
                                taxes_f = self._update_sii_tax_line(
                                    taxes_f, tax_line, line,
                                    line.invoice_line_tax_ids)
                    # TODO l10n_es no dispone de NoSujetas de bienes
                if tax_line in taxes_sfess or tax_line in taxes_sfesse or \
                    tax_line in taxes_sfens or tax_line in taxes_sfesbee or \
                        tax_line in taxes_sfesbei:
                    if 'DesgloseTipoOperacion' not in taxes_sii:
                        taxes_sii['DesgloseTipoOperacion'] = {}
                    type_breakdown = taxes_sii['DesgloseTipoOperacion']
                    if tax_line in taxes_sfess or \
                            tax_line in taxes_sfesse or \
                            tax_line in taxes_sfens:
                        if 'PrestacionServicios' not in type_breakdown:
                            type_breakdown['PrestacionServicios'] = {}
                        op_key = 'PrestacionServicios'
                    if tax_line in taxes_sfesbee or tax_line in taxes_sfesbei:
                        if 'Entrega' not in type_breakdown:
                            type_breakdown['Entrega'] = {}
                        op_key = 'Entrega'
                    if tax_line in taxes_sfens:
                        if 'NoSujeta' not in inv_breakdown:
                            type_breakdown[op_key]['NoSujeta'] = {}
                            type_breakdown[op_key]['NoSujeta'][
                                'ImportePorArticulos7_14_Otros'] = \
                                line.price_subtotal
                        else:
                            type_breakdown[op_key]['NoSujeta'][
                                'ImportePorArticulos7_14_Otros'] += \
                                line.price_subtotal
                    else:
                        if 'Sujeta' not in type_breakdown[op_key]:
                            type_breakdown[op_key]['Sujeta'] = {}
                    if tax_line in taxes_sfesse or \
                            tax_line in taxes_sfesbee or \
                            tax_line in taxes_sfesbei:
                        if 'Exenta' not in type_breakdown[op_key]['Sujeta']:
                            type_breakdown[op_key]['Sujeta']['Exenta'] = {}
                            type_breakdown[op_key]['Sujeta']['Exenta'][
                                'DetalleExenta'] = {
                                    'BaseImponible': line.price_subtotal}
                            if tax_line in taxes_sfesbee:
                                type_breakdown[op_key]['Sujeta']['Exenta'][
                                    'DetalleExenta']['CausaExencion'] = 'E2'
                            if tax_line in taxes_sfesbei:
                                type_breakdown[op_key]['Sujeta']['Exenta'][
                                    'DetalleExenta']['CausaExencion'] = 'E5'
                        else:
                            type_breakdown[op_key]['Sujeta']['Exenta'][
                                'DetalleExenta'][
                                    'BaseImponible'] += line.price_subtotal
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
                            tax_type = tax_line.amount * 100
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
            for key, line in taxes_f.items():
                if self.type == 'out_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaRepercutida', False):
                        line['CuotaRepercutida'] = \
                            -round(line['CuotaRepercutida'], 2)
                        line['BaseImponible'] = -round(
                            line['BaseImponible'], 2)
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
            for key, line in taxes_to.items():
                if self.type == 'out_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    line['CuotaRepercutida'] = \
                        -round(line['CuotaRepercutida'], 2)
                    line['BaseImponible'] = -round(line['BaseImponible'], 2)
                taxes_sii['DesgloseTipoOperacion']['PrestacionServicios'][
                    'Sujeta']['NoExenta']['DesgloseIVA'][
                    'DetalleIVA'].append(line)
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
                        tax_type = tax_line.amount * 100
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
                        tax_type = tax_line.amount * 100
                        if str(tax_type) not in taxes_f:
                            taxes_f[str(tax_type)] = self._get_sii_tax_line(
                                tax_line, line, line.invoice_line_tax_ids)
                        else:
                            taxes_f = self._update_sii_tax_line(
                                taxes_f, tax_line, line,
                                line.invoice_line_tax_ids)
        if len(taxes_f) > 0:
            for key, line in taxes_f.items():
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
            for key, line in taxes_isp.items():
                if self.type == 'in_refund' and self.refund_type == 'I':
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            -round(line['CuotaRecargoEquivalencia'], 2)
                    if line.get('CuotaSoportada', False):
                        line['CuotaSoportada'] = \
                            -round(line['CuotaSoportada'], 2)
                else:
                    if line.get('CuotaRecargoEquivalencia', False):
                        line['CuotaRecargoEquivalencia'] = \
                            round(line['CuotaRecargoEquivalencia'], 2)
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
    def _get_invoices(self):
        self.ensure_one()
        sii_map = self._get_sii_map()
        if not self.partner_id.vat:
            raise UserError(
                "The partner has not a VAT configured.")
        invoice_date = self._change_date_format(self.date_invoice)
        company = self.company_id
        ejercicio = fields.Date.from_string(
            self.date_invoice).year
        periodo = '%02d' % fields.Date.from_string(
            self.date_invoice).month
        if not company.chart_template_id:
            raise UserError(_(
                'You have to select what account chart template use this'
                ' company.'))
        key = self.registration_key.code
        tipo_factura = self._get_tipo_factura()
        if self.partner_id.is_company:
            nombrerazon = self.partner_id.name[0:120]
        else:
            nombrerazon = self.partner_id.parent_id.name[0:120]
        if self.type in ['out_invoice', 'out_refund']:
            tipo_desglose = self._get_sii_out_taxes()
            if self.type == 'out_refund' and self.refund_type == 'I':
                    importe_total = -abs(self.amount_total)
            else:
                importe_total = self.amount_total
            invoices = {
                "IDFactura": {
                    "IDEmisorFactura": {
                        "NIF": company.vat[2:]
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

        if self.type in ['in_invoice', 'in_refund']:
            desglose_factura = self._get_sii_in_taxes()
            cuota_deducible = 0
            if 'DesgloseIVA' in desglose_factura:
                for desglose in desglose_factura['DesgloseIVA']['DetalleIVA']:
                    cuota_deducible += desglose['CuotaSoportada']
            reg_date = self._change_date_format(
                self.sii_registration_date or fields.Date.today())
            if self.type == 'in_refund' and self.refund_type == 'I':
                    importe_total = -abs(self.amount_total)
            else:
                importe_total = self.amount_total
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
    def _send_invoice_to_sii(self):
        for invoice in self.filtered(
                lambda i: i.state in ['open', 'paid'] and i.is_sii_mapped):
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
                    self.sii_csv = res['CSV']
                    if 'FechaRegContable' in invoices:
                        if not self.sii_registration_date:
                            self.sii_registration_date = \
                                self._change_date_format(fields.Date.today())
                else:
                    self.sii_sent = False
                self.env['aeat.sii.result'].create_result(
                    invoice, res, 'normal', False, 'account.invoice')
                send_error = False
                res_line = res['RespuestaLinea'][0]
                if res_line['CodigoErrorRegistro']:
                    send_error = u"{} | {}".format(
                        unicode(res_line['CodigoErrorRegistro']),
                        unicode(res_line['DescripcionErrorRegistro'])[:60])
                self.sii_send_error = send_error
            except Exception as fault:
                self.env['aeat.sii.result'].create_result(
                    invoice, False, 'normal', fault, 'account.invoice')
                self.sii_send_error = fault

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
                    payment = {
                        "IDFactura": {
                            "IDEmisorFactura": {
                                "NIF": invoice.company_id.vat[2:]
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
                self.env['aeat.sii.result'].create_result(
                    invoice, res, 'recc', False, 'account.invoice')
                send_recc_error = False
                res_line = res['RespuestaLinea'][0]
                if res_line['CodigoErrorRegistro']:
                    send_recc_error = u"{} | {}".format(
                        unicode(res_line['CodigoErrorRegistro']),
                        unicode(res_line['DescripcionErrorRegistro'])[:60])
                invoice.sii_recc_send_error = send_recc_error
            except Exception as fault:
                self.env['aeat.sii.result'].create_result(
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
        return dic_ret

    @api.multi
    def _get_sii_identifier(self):
        self.ensure_one()
        dic_ret = {}
        vat = ''.join(e for e in self.partner_id.vat if e.isalnum()).upper()
        if self.fiscal_position_id.name == u'Régimen Intracomunitario':
            dic_ret = {
                "IDOtro": {
                    "CodigoPais":
                        self.partner_id.country_id and
                        self.partner_id.country_id.code or
                        vat[:2],
                    "IDType": '02',
                    "ID": vat
                }
            }
            dic_ret = self._fix_country_code(dic_ret)
        elif self.fiscal_position_id.name == \
                u'Régimen Extracomunitario / Canarias, Ceuta y Melilla':
            if vat[:2] == 'ES':
                _logger.info("Canarias")
                dic_ret = {"NIF": self.partner_id.vat[2:]}
            else:
                _logger.info("Otro")
                dic_ret = {
                    "IDOtro": {
                        "CodigoPais":
                            self.partner_id.country_id and
                            self.partner_id.country_id.code or
                            vat[:2],
                        "IDType": '04',
                        "ID": vat
                      }
                }
            dic_ret = self._fix_country_code(dic_ret)
        elif vat.startswith('ESN'):
            dic_ret = {"NIF": self.partner_id.vat[2:]}
        else:
            dic_ret = {"NIF": self.partner_id.vat[2:]}
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
                self.date_invoice).year
            periodo = '%02d' % fields.Date.from_string(
                self.date_invoice).month
            invoice_date = self._change_date_format(invoice.date_invoice)
            try:
                query = {
                    "PeriodoImpositivo": {
                        "Ejercicio": ejercicio,
                        "Periodo": periodo
                    },
                    "IDFactura": {
                        "NumSerieFacturaEmisor": number,
                        "FechaExpedicionFacturaEmisor": invoice_date
                    }
                }
                res = invoice._send_soap(
                    wsdl, port_name, operation, header, query)
                self.env['aeat.check.sii.result'].create_result(
                    invoice, res, False, 'account.invoice')
            except Exception as fault:
                self.env['aeat.check.sii.result'].create_result(
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
    def send_recc_payment_job(self, move):
        if move.exists() and move.invoice:
            move.invoice.send_recc_payment_registry(move)
