# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
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

from osv import osv, fields
from datetime import datetime
from tools.translate import _
from log import *

class csb_19(osv.osv):
    _inherit = 'csb.19'
    
    def _extra_opcional_19(self,cr,uid, recibo):
        """Para poner los 15 conceptos opcional de los registros 5681-5685 utilizando las lineas de facturación (Máximo 15 lineas)"""
        converter = self.pool.get('payment.converter.spain')
        res = {}
        res['texto'] = ''
        res['total_lines'] = 0
        counter = 1
        registry_counter = 1
        lenght = 0
        for invoice in recibo['ml_inv_ref']:
            if invoice:
                lenght += len(invoice.invoice_line)
        for invoice in recibo['ml_inv_ref']:
            if invoice:
                for invoice_line in invoice.invoice_line:
                    if counter <= lenght:
                        if counter <= 15:
                            if (counter-1)%3 == 0:
                                res['texto'] += '568'+str(registry_counter)
                                res['texto'] += (self.order.mode.bank_id.partner_id.vat[2:] + self.order.mode.sufijo).zfill(12)
                                res['texto'] += str(recibo['name']).zfill(12)
                            price = ' %(#).2f ' % {'#' : invoice_line.price_subtotal}
                            
                            if invoice_line.meter_parent_line_id:
                                if invoice_line.meter_parent_line_id.product_id.meters == 1:
                                    res['texto'] += converter.to_ascii(cr,uid,invoice_line.name)[0:40].ljust(40)
                                else:
                                    res['texto'] += converter.to_ascii(cr,uid,invoice_line.name)[0:(40-len(price))].ljust(40-len(price))
                                    res['texto'] += converter.to_ascii(cr,uid,price.replace('.',','))
                            else:
                                res['texto'] += converter.to_ascii(cr,uid,invoice_line.name)[0:(40-len(price))].ljust(40-len(price))
                                res['texto'] += converter.to_ascii(cr,uid,price.replace('.',','))
                                
                            if counter % 3 == 0:
                                res['texto'] += 14*' '+'\r\n'
                                res['total_lines'] += 1
                                if len(res['texto']) != registry_counter*164:
                                    raise Log(_('Configuration error:\n\nThe line "%s" is not 162 characters long:\n%s') % ('Individual opcional 19', res['texto']), True)
                                registry_counter += 1
                            elif counter == lenght:
                                res['texto'] += (3-(counter % 3))*40*' '+14*' '+'\r\n'
                                res['total_lines'] += 1
                                if len(res['texto']) != registry_counter*164:
                                    raise Log(_('Configuration error:\n\nThe line "%s" is not 162 characters long:\n%s') % ('Individual opcional 19', res['texto']), True)
                            counter += 1
        return res
    
csb_19()