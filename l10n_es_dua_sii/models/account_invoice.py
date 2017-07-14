# -*- coding: utf-8 -*-
# Copyright (c) 2017 Consultoría Informática Studio 73 S.L.
# Copyright (c) 2017 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from osv import osv, fields


class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'is_dua': fields.boolean(string='Is dua'),
    }

    def _get_invoices(self, cr, uid, company, invoice):
        """
        Según la documentación de la AEAT, la operación de importación se
        registra con TipoFactura = F5, sin FechaOperacion y con el NIF de la
        propia compañia en IDEmisorFactura y Contraparte
        Más información en: 8.1.2.2.Ejemplo mensaje XML de alta de importación
        en el documento de descripción de los servicios web:
        http://bit.ly/2rGWiAI

        """
        res = super(AccountInvoice, self)._get_invoices(
            cr, uid, company, invoice)
        if res.get('FacturaRecibida', False):
            if invoice.is_dua:
                res['FacturaRecibida']['TipoFactura'] = 'F5'
                res['FacturaRecibida'].pop('FechaOperacion', None)
                res['FacturaRecibida']['IDEmisorFactura'] = \
                    {'NIF': invoice.company_id.partner_id.vat[2:]}
                res['IDFactura']['IDEmisorFactura'] = \
                    {'NIF': invoice.company_id.partner_id.vat[2:]}
                res['FacturaRecibida']['Contraparte']['NIF'] = \
                    invoice.company_id.partner_id.vat[2:]
                res['FacturaRecibida']['Contraparte']['NombreRazon'] = \
                    invoice.company_id.name
            if invoice.registration_key.code == '13':
                res['FacturaRecibida']['TipoFactura'] = 'F6'
        return res

AccountInvoice()
