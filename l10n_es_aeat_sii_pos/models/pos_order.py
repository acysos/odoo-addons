# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import models, exceptions, fields, api, _
from odoo.modules.registry import Registry
from datetime import datetime
from requests import Session

_logger = logging.getLogger(__name__)

try:
    from zeep import Client
    from zeep.transports import Transport
    from zeep.plugins import HistoryPlugin
except (ImportError, IOError) as err:
    _logger.debug(err)

try:
    from odoo.addons.connector.queue.job import job
    from odoo.addons.connector.session import ConnectorSession
except ImportError:
    _logger.debug('Can not `import connector`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_default_sii_description(self):
        company = self.env.user.company_id
        method_desc = company.sii_description_method
        header_sale = company.sii_header_sale
        fixed_desc = company.sii_description
        description = '/'
        if header_sale:
            description = header_sale
        if method_desc in ['fixed']:
            description += fixed_desc
        return description

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
        comodel_name='aeat.sii.result', inverse_name='pos_order_id',
        string='POS order results')
    sii_send_error = fields.Text(string='SII Send Error')
    simplified_jobs_ids = fields.Many2many(
        comodel_name='queue.job', column1='pos_order_id', column2='job_id',
        string="POS Order Jobs", copy=False)
    sii_enabled = fields.Boolean(string='Enable SII',
                                 related='company_id.sii_enabled')
    sii_reconcile_state = fields.Selection(RECONCILE, string='Reconcile State',
                                           readonly=True, index=True)
    sii_check_results = fields.One2many(
        comodel_name='aeat.check.sii.result', inverse_name='pos_order_id',
        string='Check results')

    @api.multi
    def _get_sii_map(self):
        sii_map_obj = self.env['aeat.sii.map']
        sii_map_line_obj = self.env['aeat.sii.map.lines']
        sii_map = sii_map_obj.search(
            ['|',
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
    def _get_header(self, tipo_comunicacion, sii_map):
        self.ensure_one()
        company = self.company_id
        if not company.vat:
            raise exceptions.Warning(_(
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
    def _change_date_format(self, date):
        datetimeobject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        new_date = datetimeobject.strftime('%d-%m-%Y')
        return new_date

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
    def _get_line_price_subtotal(self, line):
        self.ensure_one()
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        return price

    @api.multi
    def _get_sii_tax_line(self, tax_line, line, line_taxes):
        self.ensure_one()
        tax_type = tax_line.amount
        taxes = tax_line.compute_all(
            price_unit=self._get_line_price_subtotal(line),
            quantity=line.qty, product=line.product_id,
            partner=line.order_id.partner_id)
        tax_sii = {
            "TipoImpositivo": tax_type,
            "BaseImponible": taxes['total_excluded'],
            'CuotaRepercutida': taxes['taxes'][0]['amount']
        }

        return tax_sii

    @api.multi
    def _update_sii_tax_line(self, tax_sii, tax_line, line, line_taxes):
        self.ensure_one()
        tax_type = tax_line.amount * 100
        taxes = tax_line.compute_all(
            self._get_line_price_subtotal(line),
            line.qty, line.product_id, line.order_id.partner_id)

        tax_sii[str(tax_type)]['BaseImponible'] += taxes['total']
        tax_sii[str(tax_type)]['CuotaRepercutida'] += \
            taxes['taxes'][0]['amount']
        return tax_sii

    @api.multi
    def _get_sii_out_taxes(self):
        self.ensure_one()
        taxes_sii = {}
        taxes_f = {}
        taxes_to = {}
        taxes_sfesb = self._get_taxes_map(['SFESB'])
        taxes_sfess = self._get_taxes_map(['SFESS'])
        for line in self.lines:
            for tax_line in line.tax_ids:
                if tax_line in taxes_sfesb:
                    if 'DesgloseFactura' not in taxes_sii:
                        taxes_sii['DesgloseFactura'] = {}
                    inv_breakdown = taxes_sii['DesgloseFactura']
                    if 'Sujeta' not in inv_breakdown:
                        inv_breakdown['Sujeta'] = {}

                    if tax_line in taxes_sfesb:
                        if 'NoExenta' not in inv_breakdown[
                                'Sujeta']:
                            inv_breakdown['Sujeta'][
                                'NoExenta'] = {}
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
                                    line.tax_ids)
                        else:
                            taxes_f = self._update_sii_tax_line(
                                taxes_f, tax_line, line,
                                line.tax_ids)

                if tax_line in taxes_sfess:
                    if 'DesgloseTipoOperacion' not in taxes_sii:
                        taxes_sii['DesgloseTipoOperacion'] = {}
                    type_breakdown = taxes_sii['DesgloseTipoOperacion']
                    if 'PrestacionServicios' not in type_breakdown:
                        type_breakdown['PrestacionServicios'] = {}
                    op_key = 'PrestacionServicios'
                    if 'Sujeta' not in type_breakdown[op_key]:
                        type_breakdown[op_key]['Sujeta'] = {}
                    if 'NoExenta' not in type_breakdown[
                            'PrestacionServicios']['Sujeta']:
                        type_breakdown['PrestacionServicios'][
                            'Sujeta']['NoExenta'] = {}
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
                                    line.tax_ids)
                        else:
                            taxes_to = self._update_sii_tax_line(
                                taxes_to, tax_line, line,
                                line.tax_ids)

        if len(taxes_f) > 0:
            for key, line in taxes_f.items():
                if line.get('CuotaRepercutida', False):
                    line['CuotaRepercutida'] = \
                        round(line['CuotaRepercutida'], 2)
                if line.get('TipoImpositivo', False):
                    line['TipoImpositivo'] = round(line['TipoImpositivo'], 2)
                taxes_sii['DesgloseFactura']['Sujeta']['NoExenta'][
                    'DesgloseIVA']['DetalleIVA'].append(line)
        if len(taxes_to) > 0:
            for key, line in taxes_to.items():
                taxes_sii['DesgloseTipoOperacion']['PrestacionServicios'][
                    'Sujeta']['NoExenta']['DesgloseIVA'][
                    'DetalleIVA'].append(line)
        return taxes_sii

    @api.multi
    def _get_simplified(self):
        self.ensure_one()
        sii_map = self._get_sii_map()
        order_date = self._change_date_format(self.date_order)
        company = self.company_id
        ejercicio = fields.Date.from_string(
            self.date_order).year
        periodo = '%02d' % fields.Date.from_string(
            self.date_order).month
        if not company.chart_template_id:
            raise exceptions.Warning(_(
                'You have to select what account chart template use this'
                ' company.'))
        key = '01'
        if self.amount_total < 0:
            tipo_factura = 'R5'
        else:
            tipo_factura = 'F2'
        tipo_desglose = self._get_sii_out_taxes()
        importe_total = self.amount_total
        orders = {
            "IDFactura": {
                "IDEmisorFactura": {
                    "NIF": company.vat[2:]
                },
                "NumSerieFacturaEmisor": self.name[0:60],
                "FechaExpedicionFacturaEmisor": order_date},
            "FacturaExpedida": {
                "TipoFactura": tipo_factura,
                "ClaveRegimenEspecialOTrascendencia": key,
                "DescripcionOperacion": self.sii_description[0:500],
                "TipoDesglose": tipo_desglose,
                "ImporteTotal": importe_total
            }
        }

        if sii_map.version == '1.0':
            orders['PeriodoImpositivo'] = {
                "Ejercicio": ejercicio,
                "Periodo": periodo
            }
        else:
            orders['PeriodoLiquidacion'] = {
                "Ejercicio": ejercicio,
                "Periodo": periodo
            }

        if self.partner_id:
            orders['FacturaExpedida']['Contraparte'] = {
                "NombreRazon": self.partner_id.name[0:120]
            }
            if self.partner_id.vat:
                orders['FacturaExpedida']['Contraparte']['NIF'] = \
                    self.partner_id.vat[2:]

        if self.amount_total < 0:
            orders['FacturaExpedida'][
                'TipoRectificativa'] = 'I'

        return orders

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
        company = self.company_id
        client = self._connect_sii(wsdl)
        if company.sii_test:
            port_name += 'Pruebas'
        serv = client.bind('siiService', port_name)
        return serv

    @api.multi
    def _send_soap(self, wsdl, port_name, operation, param1, param2):
        self.ensure_one()
        serv = self._connect_wsdl(wsdl, port_name)
        res = serv[operation](param1, param2)
        return res

    @api.multi
    def _send_simplified_to_sii(self):
        for order in self.filtered(lambda i: i.state in ['done', 'paid']):
            sii_map = order._get_sii_map()
            wsdl = sii_map._get_wsdl('wsdl_out')
            port_name = 'SuministroFactEmitidas'
            operation = 'SuministroLRFacturasEmitidas'
            if not order.sii_sent:
                tipo_comunicacion = 'A0'
            else:
                tipo_comunicacion = 'A1'
            header = order._get_header(tipo_comunicacion, sii_map)
            orders = order._get_simplified()

            try:
                res = order._send_soap(
                    wsdl, port_name, operation, header, orders)
                if res['EstadoEnvio'] in ['Correcto', 'ParcialmenteCorrecto']:
                    self.sii_sent = True
                    self.sii_csv = res['CSV']
                else:
                    self.sii_sent = False
                self.env['aeat.sii.result'].create_result(
                    order, res, 'normal', False, 'pos.order')
                send_error = False
                res_line = res['RespuestaLinea'][0]
                if res_line['CodigoErrorRegistro']:
                    send_error = u"{} | {}".format(
                        unicode(res_line['CodigoErrorRegistro']),
                        unicode(res_line['DescripcionErrorRegistro'])[:60])
                self.sii_send_error = send_error
            except Exception as fault:
                self.env['aeat.sii.result'].create_result(
                    order, False, 'normal', fault, 'pos.order')
                self.sii_send_error = fault

    @api.multi
    def send_sii(self):
        queue_obj = self.env['queue.job']
        for order in self:
            company = order.company_id
            if company.sii_enabled and company.sii_method == 'auto':
                if not company.use_connector:
                    order._send_simplified_to_sii()
                else:
                    eta = company._get_sii_eta()
                    session = ConnectorSession.from_env(self.env)
                    new_delay = confirm_one_simplified.delay(
                        session, 'pos.order', order.id, eta=eta)
                    queue_ids = queue_obj.search([
                        ('uuid', '=', new_delay)
                    ], limit=1)
                    order.simplified_jobs_ids |= queue_ids

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrder, self).create_from_ui(orders)
        for order in self.browse(res):
            order.send_sii()
        return res

    @api.multi
    def _check_simplified(self):
        """ Request information to AEAT """
        for order in self.filtered(lambda i: i.state in ['done', 'paid']):
            sii_map = order._get_sii_map()
            wsdl = sii_map._get_wsdl('wsdl_out')
            port_name = 'SuministroFactEmitidas'
            operation = 'ConsultaLRFacturasEmitidas'
            number = order.name[0:60]
            header = order._get_header(False, sii_map)
            ejercicio = fields.Date.from_string(order.date_order).year
            periodo = '%02d' % fields.Date.from_string(order.date_order).month
            order_date = self._change_date_format(self.date_order)
            try:
                query = {
                    "PeriodoImpositivo": {
                        "Ejercicio": ejercicio,
                        "Periodo": periodo
                    },
                    "IDFactura": {
                        "NumSerieFacturaEmisor": number,
                        "FechaExpedicionFacturaEmisor": order_date
                    }
                }
                res = order._send_soap(
                    wsdl, port_name, operation, header, query)
                self.env['aeat.check.sii.result'].create_result(
                    order, res, False, 'pos.order')
            except Exception as fault:
                self.env['aeat.check.sii.result'].create_result(
                    order, False, fault, 'pos.order')

    @api.multi
    def check_sii(self):
        queue_obj = self.env['queue.job']
        for order in self:
            company = order.company_id
            if company.sii_enabled:
                if not company.use_connector:
                    order._check_simplified()
                else:
                    eta = company._get_sii_eta()
                    session = ConnectorSession.from_env(self.env)
                    new_delay = check_one_simplified.delay(
                        session, 'pos.order', order.id, eta=eta)
                    queue_ids = queue_obj.search([
                        ('uuid', '=', new_delay)
                    ], limit=1)
                    order.simplified_jobs_ids |= queue_ids


@job(default_channel='root.simplified_validate_sii')
def confirm_one_simplified(session, model_name, order_id):
    model = session.env[model_name]
    order = model.browse(order_id)

    order._send_simplified_to_sii()
    session.cr.commit()


@job(default_channel='root.invoice_check_sii')
def check_one_simplified(session, model_name, order_id):
    model = session.env[model_name]
    order = model.browse(order_id)

    order._check_simplified()
    session.cr.commit()
