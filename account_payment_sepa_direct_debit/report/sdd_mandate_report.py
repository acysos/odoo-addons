# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw

class sdd_mandate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sdd_mandate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'sdd_mandate_type': self._sdd_mandate_type
        })
        
    def _sdd_mandate_type(self, mandate):

        mandate_type = ''

        if mandate.type:
            mandate_type = dict(self.pool.get('sdd.mandate').fields_get(self.cr, self.uid, allfields=['type'], context=self.localcontext)['type']['selection'])[mandate.type]
        
        return mandate_type
    
report_sxw.report_sxw(
    'report.sdd.mandate',
    'sdd.mandate',
    'addons/account_payment_sepa_direct_debit/report/sdd_mandate_report.rml',
    parser=sdd_mandate
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
