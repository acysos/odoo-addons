# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
import datetime


class AeatSiiResult(models.Model):
    _name = 'aeat.sii.result'

    TYPE = [('normal', 'Normal'),
            ('recc', 'RECC')]

    csv = fields.Char(string='CSV')
    vat_presenter = fields.Char(string='Vat Presenter')
    timestamp_presentation = fields.Datetime(string='Timestamp Presentation')
    id_version_sii = fields.Char(string='ID Version SII')
    name = fields.Char(string='Company Name')
    vat_agent = fields.Char(string='Vat Agent')
    vat = fields.Char(string='Vat')
    type_communication = fields.Char(string='Type Communication')
    sent_state = fields.Char(string='Sent State')
    vat_emitting = fields.Char(string='Vat Emitting')
    country_code = fields.Char(string='Country Code')
    type_id = fields.Char(string='Type ID')
    number_id = fields.Char(string='ID')
    serial_number = fields.Char(string='Serial number')
    serial_number_resume = fields.Char(string='Serial number end resume')
    date = fields.Date(string='Date Invoice')
    registry_state = fields.Char(string='Registry State')
    registry_error_code = fields.Char(string='Registry Error Code')
    registry_error_description = fields.Char(
        string='Registry Error Description')
    registry_csv = fields.Char(string='CSV')
    inv_type = fields.Selection(TYPE, 'Type')
    invoice_id = fields.Many2one(comodel_name='account.move',
                                 string='Invoice')
    duplicate_registry_state = fields.Char(string='State')
    duplicate_registry_error_code = fields.Char(string='Error code')
    duplicate_registry_error_des = fields.Char(string='Error description')

    _order = 'id desc'

    def _prepare_vals(self, model_id, res, inv_type, fault, model):
        vals = {
            'csv': False,
            'vat_presenter': False,
            'timestamp_presentation': False,
            'id_version_sii': False,
            'name': False,
            'vat_agent': False,
            'vat': False,
            'type_communication': False,
            'sent_state': False,
            'vat_emitting': False,
            'country_code': False,
            'type_id': False,
            'number_id': False,
            'serial_number': False,
            'serial_number_resume': False,
            'date': False,
            'registry_state': False,
            'registry_error_code': False,
            'registry_error_description': False,
            'registry_csv': False,
            'inv_type': inv_type,
            'duplicate_registry_state': False,
            'duplicate_registry_error_code': False,
            'duplicate_registry_error_des': False,
        }
        if model == 'account.move':
            vals['invoice_id'] = model_id.id
        if fault:
            vals['registry_error_description'] = fault
        else:
            if 'CSV' in res:
                vals['csv'] = res['CSV']
            if 'DatosPresentacion' in res and res['DatosPresentacion']:
                if 'NIFPresentador' in res['DatosPresentacion']:
                    vals['vat_presenter'] = res[
                        'DatosPresentacion']['NIFPresentador']
                if 'TimestampPresentacion' in res['DatosPresentacion']:
                    date = datetime.datetime.strptime(
                        res['DatosPresentacion']['TimestampPresentacion'],
                        '%d-%m-%Y %H:%M:%S')
                    new_date = datetime.datetime.strftime(
                        date, '%Y-%m-%d %H:%M:%S')
                    vals['timestamp_presentation'] = new_date
            if 'Cabecera' in res:
                if 'IDVersionSii' in res['Cabecera']:
                    vals['id_version_sii'] = res['Cabecera']['IDVersionSii']
                if 'Titular' in res['Cabecera']:
                    if 'NombreRazon' in res['Cabecera']['Titular']:
                        vals['name'] = res['Cabecera']['Titular'][
                            'NombreRazon']
                    if 'NIFRepresentante' in res['Cabecera']['Titular']:
                        vals['vat_agent'] = res['Cabecera']['Titular'][
                            'NIFRepresentante']
                    if 'NIF' in res['Cabecera']['Titular']:
                        vals['vat'] = res['Cabecera']['Titular']['NIF']
                if 'TipoComunicacion' in res['Cabecera']:
                    vals['type_communication'] = res['Cabecera'][
                        'TipoComunicacion']
            if 'EstadoEnvio' in res:
                vals['sent_state'] = res['EstadoEnvio']
            if 'RespuestaLinea' in res:
                reply = res['RespuestaLinea'][0]
                if 'IDFactura' in reply:
                    if 'IDEmisorFactura' in reply['IDFactura']:
                        if 'NIF' in reply['IDFactura']['IDEmisorFactura']:
                            vals['vat_emitting'] = \
                                reply['IDFactura']['IDEmisorFactura']['NIF']
                        if 'IDOtro' in reply['IDFactura']['IDEmisorFactura']:
                            if reply['IDFactura']['IDEmisorFactura']['IDOtro']:
                                if 'CodigoPais' in reply['IDFactura'][
                                        'IDEmisorFactura']['IDOtro']:
                                    vals['country_code'] = reply['IDFactura'][
                                        'IDEmisorFactura']['IDOtro'][
                                            'CodigoPais']
                                if 'IDType' in reply['IDFactura'][
                                        'IDEmisorFactura']['IDOtro']:
                                    vals['type_id'] = reply['IDFactura'][
                                        'IDEmisorFactura']['IDOtro']['IDType']
                                if 'ID' in reply['IDFactura'][
                                        'IDEmisorFactura']['IDOtro']:
                                    vals['number_id'] = reply['IDFactura'][
                                        'IDEmisorFactura']['IDOtro']['ID']
                    if 'NumSerieFacturaEmisor' in reply['IDFactura']:
                        vals['serial_number'] = \
                            reply['IDFactura']['NumSerieFacturaEmisor']
                    if 'NumSerieFacturaEmisorResumenFin' in reply['IDFactura']:
                        vals['serial_number_resume'] = \
                            reply['IDFactura'][
                                'NumSerieFacturaEmisorResumenFin']
                    if 'FechaExpedicionFacturaEmisor' in reply['IDFactura']:
                        date = datetime.datetime.strptime(
                            reply['IDFactura']['FechaExpedicionFacturaEmisor'],
                            '%d-%m-%Y')
                        new_date = datetime.datetime.strftime(
                            date, '%Y-%m-%d')
                        vals['date'] = new_date
                if 'EstadoRegistro' in reply:
                    vals['registry_state'] = reply['EstadoRegistro']
                if 'CodigoErrorRegistro' in reply:
                    vals['registry_error_code'] = reply['CodigoErrorRegistro']
                if 'DescripcionErrorRegistro' in reply:
                    if model_id.sii_cancel:
                        vals['registry_error_description'] = _(
                            'SII Invoice Canceled. Create a new invoice')
                    else:
                        vals['registry_error_description'] = \
                            reply['DescripcionErrorRegistro']
                if 'CSV' in reply:
                    vals['registry_csv'] = reply['CSV']
                if 'RegistroDuplicado' in reply and reply['RegistroDuplicado']:
                    duplicate = reply['RegistroDuplicado']
                    if 'EstadoRegistro' in duplicate:
                        vals['duplicate_registry_state'] = duplicate[
                            'EstadoRegistro']
                    if 'CodigoErrorRegistro' in duplicate:
                        vals['duplicate_registry_error_code'] = duplicate[
                            'CodigoErrorRegistro']
                    if 'DescripcionErrorRegistro' in duplicate:
                        vals['duplicate_registry_error_des'] = duplicate[
                            'DescripcionErrorRegistro']
        return vals

    def create_result(self, model_id, res, inv_type, fault, model):
        vals = self._prepare_vals(model_id, res, inv_type, fault, model)
        self.create(vals)
