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

import base64
import calendar
import datetime
from ftplib import FTP
import os.path
import logging
import pytz
from random import random
import tempfile
from tempfile import mkstemp
import time
import unicodedata

try:
    from mako.template import Template as MakoTemplate
except ImportError:
    logging.getLogger("import").exception("Mako package is not installed")

from osv import osv, fields
import tools
from tools.translate import _

from text2pdf import pyText2Pdf

def strip_accents(s):
    u = isinstance(s, unicode) and s or unicode(s, 'utf8')
    a = ''.join((c for c in unicodedata.normalize('NFKD', u) if unicodedata.category(c) != 'Mn'))
    return str(a)


def is_a_datetime(str0, type_='datetime'):
    if isinstance(str0, str):
        formats = {
            'datetime': '%Y-%m-%d %H:%M:%S',
            'date': '%Y-%m-%d',
            'time': '%Y-%m-%d %H:%M:%S',
        }
        try:
            if type_ == 'time':
                str0 = datetime.datetime.today().strftime(formats['date']) + ' ' + str0
            result = datetime.datetime.strptime(str0, formats[type_])
            return result
        except Exception:
            pass
    return


def format_lang(pool, cr, value, lang='en_US', digits=2, tz='America/New_York'):
    lang_obj = pool.get('res.lang')
    lang_id = lang_obj.search(cr, 1, [('code', '=', lang)], limit=1)
    if lang_id:
        lang = lang_obj.read(cr, 1, lang_id[0], ['date_format', 'time_format'])
        output_formats = {
            'datetime': '%s %s' % (lang['date_format'], lang['time_format']),
            'date': str(lang['date_format']),
            'time': str(lang['time_format']),
        }
        for type in output_formats:
            if is_a_datetime(value, type):
                if tz:
                    return pytz.timezone(tz).fromutc(is_a_datetime(value)).strftime(output_formats[type])
                else:
                    return is_a_datetime(value).strftime(output_formats[type])
        return lang_obj.format(cr, 1, lang_id, '%.' + str(digits) + 'f', value)
    return value


def _get_exception_message(exception):
    return isinstance(exception, osv.except_osv) and exception.value or exception


def _render_unicode(template_src, localdict, encoding='UTF-8'):
    template = MakoTemplate(tools.ustr(template_src), output_encoding=encoding)
    return template.render_unicode(**localdict)


def _text2pdf(string):
    tmpfilename = os.path.join(tempfile.gettempdir(), str(int(random() * 10 ** 9)))
    tmpfile = open(tmpfilename, 'w')
    tmpfile.write(string)
    tmpfile.close()
    pdf = pyText2Pdf()
    pdf._ifile = tmpfilename
    pdf.Convert()
    tmpfile_pdf = open(tmpfilename + '.pdf', 'r')
    string = tmpfile_pdf.read()
    os.remove(tmpfilename)
    os.remove(tmpfilename + '.pdf')
    return string

class ir_model_export_file_template(osv.osv):
    _inherit = 'ir.model.export.file_template'
    
    _columns = {
        'filter_type': fields.selection([('domain', 'Domain'), ('method', 'Method')], string="Filter method", required=True),
        'domain': fields.char('Filter domain', size=256),
        'filter_method': fields.char('Filter method', size=64, help="signature: method(cr, uid, context)"),
        'submodel_id': fields.many2one('ir.model', 'Object', domain=[('osv_memory', '=', False)], required=True, ondelete='cascade'),
        'submodel': fields.related('submodel_id', 'model', type='char', string='Model', readonly=True),
    }
    
    _defaults = {
        'domain': '[]',
        'filter_type': 'domain',
    }
    
    def sub_domain_get(self,cr,uid,domain,model_obj):
        return model_obj.search(cr, uid, domain)
    
    def sub_method_get(self,cr,uid,filter_method,model_obj):
        method = filter_method.split('(')
        if not (filter_method and hasattr(model_obj, method[0])):
            raise osv.except_osv(_('Error'), _("Can't find method: %s on object: %s") % (filter_method, model_obj.name))
        return eval('model_obj.'+filter_method)
    
    def _render_tab(self, cr, uid, export_file, template_part, localdict):
        """Render the output of this template in a tabular format"""
        template = []
        try:
            delimiter = eval(export_file.delimiter)
        except TypeError:
            delimiter = export_file.delimiter or ''
        # Header & Footer
        if getattr(export_file, template_part):
            template.append(self._render(cr, uid, export_file, template_part, localdict))
        # Header with fieldnames
        if template_part == 'header' and export_file.fieldnames_in_header:
            template.append(delimiter.join([tools.ustr(column.name) for column in export_file.column_ids]))
        # Body
        if template_part == 'body':
            sub_objects = localdict['object']
            if export_file.refer_to_underlying_object:
                sub_objects = eval(export_file.records, localdict)
                model_obj = self.pool.get(export_file.submodel)
                if not model_obj:
                    raise osv.except_osv(_('Error'), _("Unknown object: %s") % (export_file.submodel, ))
                if export_file.filter_type == 'domain':
                    result_ids = self.sub_domain_get(cr,uid,eval(export_file.domain),model_obj)
                elif export_file.filter_type == 'method':
                    result_ids = self.sub_method_get(cr,uid,export_file.filter_method,model_obj)
                new_sub_objects = []
                for sub_object in sub_objects:
                    if sub_object.id in result_ids:
                        new_sub_objects.append(sub_object)
                sub_objects = new_sub_objects
                
            if not isinstance(sub_objects, list):
                sub_objects = [sub_objects]
            for index, sub_object in enumerate(sub_objects):
                localdict['total_number'] = localdict['total_number'] + 1
                localdict['line_number'] = index + 1
                localdict['object'] = sub_object
                line = []
                for column in export_file.column_ids:
                    try:
                        column_value = _render_unicode(column.value or '', localdict)
                        if column.default_value and not column_value:
                            column_value = _render_unicode(column.default_value, localdict)
                        if column.column_validator:
                            validation = eval(column.column_validator, localdict)
                            if not validation:
                                try:
                                    exception_msg = _render_unicode(column.exception_msg, localdict)
                                except Exception:
                                    exception_msg = column.exception_msg
                                raise osv.except_osv(_('Error'), exception_msg)
                        column_value = tools.ustr(column_value)
                        try:
                            fillchar = eval(column.fillchar)
                        except TypeError:
                            fillchar = column.fillchar
                        if column_value:
                            if column.min_width:
                                column_value = getattr(column_value, column.justify)(column.min_width, tools.ustr(fillchar))
                            if column.max_width:
                                column_value = column_value[: column.max_width]
                        else:
                            if column.min_width:
                                column_value = fillchar*column.min_width
                        if not column.not_string and export_file.quotechar:
                            try:
                                quotechar = export_file.quotechar and eval(export_file.quotechar) or ''
                            except TypeError:
                                quotechar = export_file.quotechar
                            column_value = '%(quotechar)s%(column_value)s%(quotechar)s' % {
                                'column_value': quotechar and column_value.replace(quotechar, "\\" + quotechar) or column_value,
                                'quotechar': quotechar,
                            }
                        line.append(column_value)
                    except Exception, e:
                        raise osv.except_osv(_('Error'), 'column %s: %s' % (column.name, e))
                template.append(delimiter.join(line))
        try:
            lineterminator = eval(export_file.lineterminator)
        except TypeError:
            lineterminator = export_file.lineterminator
        return lineterminator.join(template)

    def _lay_out_data(self, cr, uid, export_file, context):
        """Call specific layout methods and catch exceptions"""
        content = []
        exceptions = []
        content_render_method = export_file.state == 'tab' and '_render_tab' or '_render'
        if content_render_method:
            localdict = {
                'pool': self.pool,
                'cr': cr,
                'uid': uid,
                'localcontext': context,
                'time': time,
                'datetime': datetime,
                'calendar': calendar,
                'format_lang': format_lang,
                'strip_accents': strip_accents,
            }
            objects = self.pool.get(export_file.model_id.model).browse(cr, uid, context['active_ids'], context)
            for template_part in ['header', 'body', 'footer']:
                if export_file.state == 'tab' and export_file.column_ids or getattr(export_file, template_part):
                    template_parts = template_part == 'body' and objects or [objects]
                    if template_part == 'body': localdict['total_number'] = 0
                    for line in template_parts:
                        localdict['object'] = line
                        try:
                            content.append(getattr(self, content_render_method)(cr, uid, export_file, template_part, localdict))
                        except Exception, e:
                            if template_part == 'body' and export_file.exception_handling == 'continue':
                                exceptions.append('%s - %s, %s: %s' % (template_part, export_file.model, line.id, _get_exception_message(e)))
                            else:
                                raise Exception('%s - %s' % (template_part, _get_exception_message(e)))
        try:
            lineterminator = eval(export_file.lineterminator)
        except TypeError:
            lineterminator = export_file.lineterminator
        return (lineterminator.join(content), exceptions)
    
ir_model_export_file_template()

class ir_model_export_file_template_column(osv.osv):
    _inherit = 'ir.model.export.file_template.column'
    
    _columns = {
        'fillchar': fields.char('Fillchar', size=24),
    }
    
ir_model_export_file_template_column()