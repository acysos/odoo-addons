# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons import decimal_precision as dp
import datetime


class AeatCheckSiiResult(models.Model):
    _name = 'aeat.check.sii.result'

    RESULTS = [('ConDatos', 'Con datos'),
               ('SinDatos', 'Sin datos')]

    RECONCILE = [('1', 'No contrastable'),
                 ('2', 'En proceso de contraste'),
                 ('3', 'No contrastada'),
                 ('4', 'Parcialmente contrastada'),
                 ('5', 'Contrastada')]

    check_date = fields.Datetime(string='Date check')
    result_query = fields.Selection(RESULTS, string='Type')
    vat = fields.Char(string='NIF')
    other_id = fields.Char(string='Other identifier')
    invoice_number = fields.Char(string='Invoice number')
    invoice_date = fields.Date(string='Invoice date')
    invoice_type = fields.Char(string='Invoice type')
    refund_type = fields.Selection(
        selection=[('S', 'By substitution'), ('I', 'By differences')],
        string="Refund Type")
    registration_key = fields.Many2one(
        comodel_name='aeat.sii.mapping.registration.keys',
        string="Registration key")
    amount_total = fields.Float(
        string='Amount total', digits=dp.get_precision('Account'))
    description = fields.Text(string='Description')
    name = fields.Char(string='Company Name')
    vat_partner = fields.Char(string='NIF')
    other_id_partner = fields.Char(string='Other identifier')
    vat_presenter = fields.Char(string='NIF')
    timestamp_presentation = fields.Datetime(string='Timestamp Presentation')
    csv = fields.Char(string='CSV')
    reconcile_state = fields.Selection(RECONCILE, string='Reconcile State')
    reconcile_timestamp = fields.Datetime(string='Reconcile Timestamp')
    timestamp_last = fields.Datetime(string='Timestamp Last Update ')
    sent_state = fields.Char(string='State')
    error_code = fields.Char(string='Error code')
    description_error = fields.Text(string='Description Error')
    reconcile_description = fields.Text(string='Reconcile description')
    registry_error_description = fields.Char(
        string='Registry Error Description')
    invoice_id = fields.Many2one(comodel_name='account.move',
                                 string='Invoice')

    def _get_data(self, model_id, res, model):
        data = {}
        key = ''
        key_type = ''
        if model == 'account.move':
            if model_id.type in ('out_invoice', 'out_refund'):
                data = res['RegistroRespuestaConsultaLRFacturasEmitidas'][0]
                key = 'DatosFacturaEmitida'
                key_type = 'sale'
            if model_id.type in ('in_invoice', 'in_refund'):
                data = res['RegistroRespuestaConsultaLRFacturasRecibidas'][0]
                key = 'DatosFacturaRecibida'
                key_type = 'purchase'
        return data, key, key_type

    def _prepare_vals(self, model_id, res, fault, model):
        vals = {
            'check_date': fields.Datetime.now()
        }
        if model == 'account.move':
            vals['invoice_id'] = model_id.id
        if fault:
            vals['registry_error_description'] = fault
        else:
            vals['result_query'] = res['ResultadoConsulta']
            data, key, key_type = self._get_data(model_id, res, model)
        if 'result_query' in vals and vals['result_query'] == 'ConDatos':
            key_obj = self.env['aeat.sii.mapping.registration.keys']
            vals['vat'] = data['IDFactura']['IDEmisorFactura']['NIF']
            if model == 'account.move':
                if model_id.type in ('in_invoice', 'in_refund'):
                    vals['other_id'] = data[
                        'IDFactura']['IDEmisorFactura']['IDOtro']
            vals['invoice_number'] = data['IDFactura']['NumSerieFacturaEmisor']
            date = datetime.datetime.strptime(
                data['IDFactura']['FechaExpedicionFacturaEmisor'],
                '%d-%m-%Y')
            new_date = datetime.datetime.strftime(
                date, '%Y-%m-%d')
            vals['invoice_date'] = new_date
            vals['invoice_type'] = data[key]['TipoFactura']
            vals['refund_type'] = data[key]['TipoRectificativa']
            registration_key = key_obj.search(
                [('code', '=', data[key][
                    'ClaveRegimenEspecialOTrascendencia']),
                 ('type', '=', key_type)]
            )
            vals['registration_key'] = registration_key.id
            vals['amount_total'] = data[key]['ImporteTotal']
            vals['description'] = data[key]['DescripcionOperacion']
            if 'Contraparte' in data[key] and data[key]['Contraparte']:
                vals['name'] = data[key]['Contraparte']['NombreRazon']
                vals['vat_partner'] = data[key]['Contraparte']['NIF']
                vals['other_id_partner'] = data[key]['Contraparte']['IDOtro']
            vals['vat_presenter'] = data['DatosPresentacion']['NIFPresentador']
            date = datetime.datetime.strptime(
                data['DatosPresentacion']['TimestampPresentacion'],
                '%d-%m-%Y %H:%M:%S')
            new_date = datetime.datetime.strftime(
                date, '%Y-%m-%d %H:%M:%S')
            vals['timestamp_presentation'] = new_date
            vals['csv'] = data['DatosPresentacion']['CSV']
            vals['reconcile_state'] = data['EstadoFactura']['EstadoCuadre']
            model_id.sii_reconcile_state = vals['reconcile_state']
            if 'TimestampEstadoCuadre' in data['EstadoFactura']:
                if data['EstadoFactura']['TimestampEstadoCuadre']:
                    date = datetime.datetime.strptime(
                        data['EstadoFactura']['TimestampEstadoCuadre'],
                        '%d-%m-%Y %H:%M:%S')
                    new_date = datetime.datetime.strftime(
                        date, '%Y-%m-%d %H:%M:%S')
                    vals['reconcile_timestamp'] = new_date
            date = datetime.datetime.strptime(
                data['EstadoFactura']['TimestampUltimaModificacion'],
                '%d-%m-%Y %H:%M:%S')
            new_date = datetime.datetime.strftime(
                date, '%Y-%m-%d %H:%M:%S')
            vals['timestamp_last'] = new_date
            vals['sent_state'] = data['EstadoFactura']['EstadoRegistro']
            vals['error_code'] = data['EstadoFactura']['CodigoErrorRegistro']
            vals['description_error'] = data[
                'EstadoFactura']['DescripcionErrorRegistro']
            vals['reconcile_description'] = data['DatosDescuadreContraparte']
        return vals

    def create_result(self, model_id, res, fault, model):
        vals = self._prepare_vals(model_id, res, fault, model)
        self.create(vals)
