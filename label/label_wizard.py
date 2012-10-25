# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2009  Sharoon Thomas (some code belongs to poweremail module)
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

import netsvc
from osv import osv, fields

from label_report_engine import size2cm

class label_wizard(osv.osv_memory):
    _name = 'label.wizard'
    _description = 'This is the wizard for create PDF Labels'
    _rec_name = "subject"

    def _lang_get(self, cr, uid, context=None):
        obj = self.pool.get('res.lang')
        ids = obj.search(cr, uid, [], context=context)
        res = obj.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res] + [('','')]

    def _default_label_format(self, cr, uid, context=None):
        tmpl_obj = self.pool.get('label.templates')
        if 'template_id' in context:
            tmpl = tmpl_obj.browse(cr, uid, int(context['template_id']))
            try:
                return tmpl.default_label_format_id.id
            except AttributeError:
                return False

    _columns = {
        'state':fields.selection([
                        ('create_report','Create a report.'),
                        ('notify_top','Printer top margin bigger than (top label margin + label height). Try again.'),
                        ('notify_bottom','Printer bottom margin bigger than (bottom label margin + label height). Try again.'),
                        ('notify_left','Printer left margin bigger than (left label margin + label width). Try again.'),
                        ('notify_right','Printer right margin bigger than (right label margin + label width). Try again.'),
                        ('done','Wizard Complete')
                                  ],'Status',readonly=True),
        'label_format': fields.many2one('report.label','Label Format', required=True),
        'printer_top' : fields.char('Top', size=20, required=True, help='Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in'),
        'printer_bottom': fields.char('Bottom', size=20, required=True, help='Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in'),
        'printer_left': fields.char('Left', size=20, required=True, help='Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in'),
        'printer_right': fields.char('Right', size=20, required=True, help='Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in'),
        'font_type': fields.selection(
            [('Times-Roman','Times-Roman'),('Times-Bold','Times-Bold'),('Times-Italic','Times-Italic'),('Times-BoldItalic','Times-BoldItalic'),('Helvetica','Helvetica'),('Helvetica-Bold','Helvetica-Bold'),('Helvetica-Oblique','Helvetica-Oblique'),('Helvetica-BoldOblique','Helvetica-BoldOblique'),('Courier','Courier'),('Courier-Bold','Courier-Bold'),('Courier-Oblique','Courier-Oblique'),('Courier-BoldOblique','Courier-BoldOblique')
            ], 'Font Type', required=True),
        'font_size': fields.selection(
            [('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('14','14')
            ], 'Font Size', required=True),
        'first_row': fields.integer('First Row',help='The Row of the first label in the first page'),
        'first_col': fields.integer('First Column',help='The Column of the first label in the first page'),
        'lang': fields.selection(_lang_get, 'Language', size=5),
        'number_labels': fields.integer('Number of labels',help='Number of label for each object'),
    }

    _defaults = {
        'state': lambda *a: 'create_report',
        'label_format': _default_label_format,
        'number_labels': 1,
    }

    def create_label(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        
        vals = self.browse(cr, uid, ids[0], context)
        vals.printer_top    = size2cm(vals.printer_top)
        vals.printer_bottom = size2cm(vals.printer_bottom)
        vals.printer_left   = size2cm(vals.printer_left)
        vals.printer_right  = size2cm(vals.printer_right)
        vals.page_width = size2cm(vals.label_format.landscape and vals.label_format.pagesize_id.height or vals.label_format.pagesize_id.width)
        vals.page_height = size2cm(vals.label_format.landscape and vals.label_format.pagesize_id.width or vals.label_format.pagesize_id.height)
        vals.rows = vals.label_format.rows
        vals.cols = vals.label_format.cols
        vals.label_width = size2cm(vals.label_format.label_width)
        vals.label_height = size2cm(vals.label_format.label_height)
        vals.width_incr = size2cm(vals.label_format.width_incr)
        vals.height_incr = size2cm(vals.label_format.height_incr)
        vals.initial_left_pos = size2cm(vals.label_format.margin_left)

        # initial_bottom_pos = label.pagesize_id.height - label.margin_top - label.label_height
        mtop = size2cm(vals.label_format.margin_top)
        vals.initial_bottom_pos = vals.page_height - mtop - vals.label_height

        validate = False

        if vals.printer_top > mtop + vals.label_height:
            self.write(cr, uid, ids, {'state':'notify_top'}, context)
            validate = True
        if vals.printer_left > vals.initial_left_pos + vals.label_width:
            self.write(cr, uid, ids, {'state':'notify_left'}, context)
            validate = True
        if vals.printer_bottom > vals.page_height - mtop - (vals.rows-1) * vals.height_incr:
            self.write(cr, uid, ids, {'state':'notify_bottom'}, context)
            validate = True
        if vals.printer_right >  vals.page_width - vals.initial_left_pos - (vals.cols-1) * vals.width_incr:
            self.write(cr, uid, ids, {'state':'notify_right'}, context)
            validate = True

        if not validate:
            template_obj = self.pool.get('label.templates')
            template = template_obj.browse(cr, uid, int(context['template_id']))
            report_full_name = 'report.'+template.report_template.report_name
            if report_full_name in netsvc.Service._services:
                del netsvc.Service._services[report_full_name]
            template_obj.instantiate_report(template)

            #datas dictionary should work with client >= 5.0.12 (see https://answers.launchpad.net/openobject-server/+question/116262)
            #but web client seems not receiving datas information
            if vals.lang:
                context['lang'] = vals.lang
            datas = {}
            datas['context'] = context.copy()
            datas['ids'] = ids
            
            res =  {
                'type': 'ir.actions.report.xml',
                'report_name': template.report_template.report_name,
                'datas': datas,
                'context': context,
                'nodestroy': True
            }
            return res

label_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
