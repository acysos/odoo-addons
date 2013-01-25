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

import threading
import time

from osv import osv, fields
import pooler
import tools
from tools.translate import _

from smile_log.db_handler import SmileDBLogger

class ir_model_export_template(osv.osv):
    _inherit = 'ir.model.export.template'
    
    def _get_res_ids(self, cr, uid, template, context):
        context = context or {}
        res_ids = context.get('resource_ids_to_export', [])
        model_obj = self.pool.get(template.model)
        if not model_obj:
            raise osv.except_osv(_('Error'), _("Unknown object: %s") % (template.model, ))
        if template.filter_type == 'domain':
            domain = eval(template.domain)
            if res_ids:
                domain.append(('id', 'in', res_ids))
            res_ids = model_obj.search(cr, uid, domain, context=context)
        elif template.filter_type == 'method':
            method = template.filter_method.split('(')
            if not (template.filter_method and hasattr(model_obj, method[0])):
                raise osv.except_osv(_('Error'), _("Can't find method: %s on object: %s") % (template.filter_method, template.model))
            context['ir_model_export_template_id'] = template.id
            res_ids2 = eval('model_obj.'+template.filter_method)
            return res_ids and list(set(res_ids) & set(res_ids2)) or res_ids2
        if template.export_file_template_id.refer_to_underlying_object:
            submodel_obj = self.pool.get(template.export_file_template_id.submodel)
            if not model_obj:
                raise osv.except_osv(_('Error'), _("Unknown object: %s") % (template.export_file_template_id.submodel))
            if template.export_file_template_id.filter_type == 'domain':
                result_ids = self.pool.get('ir.model.export.file_template').sub_domain_get(cr,uid,eval(template.export_file_template_id.domain),submodel_obj)
            elif template.export_file_template_id.filter_type == 'method':
                result_ids = self.pool.get('ir.model.export.file_template').sub_method_get(cr,uid,template.export_file_template_id.filter_method,submodel_obj)
            if len(result_ids) == 0:
                res_ids = []
            else:
                new_res_ids = []
                field_record = template.export_file_template_id.records.split('.')[-1]
                for res_id in res_ids:
                    res_obj = model_obj.browse(cr,uid,res_id,context)
                    for sub_res_obj in eval('res_obj.'+field_record):
                        if sub_res_obj.id in result_ids:
                            if not res_id in new_res_ids:
                                new_res_ids.append(res_id)
            res_ids = new_res_ids
        return res_ids
    
ir_model_export_template()