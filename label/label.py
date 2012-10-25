# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2009  Sharoon Thomas (some code has been copied from poweremail module)
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
from tools import config
import netsvc
import random
import os
import re

LOGGER = netsvc.Logger()

TEMPLATE_ENGINES = []

from tools.translate import _
#Try and check the available templating engines
from mako.template import Template  #For backward combatibility
try:
    from mako.template import Template as MakoTemplate
    from mako import exceptions
    TEMPLATE_ENGINES.append(('mako', 'Mako Templates'))
except:
    LOGGER.notifyChannel(
                         _("Label"),
                         netsvc.LOG_ERROR,
                         _("Mako templates not installed")
                         )
import report
import pooler
import label_report_engine

class label_templates(osv.osv):
    "Templates for Labels"

    _name = "label.templates"
    _description = 'Label Templates for Models'

    def change_model(self, cr, uid, ids, object_name, context=None):
        if object_name:
            mod_name = self.pool.get('ir.model').read(cr, uid, object_name, ['model'], context)['model']
        else:
            mod_name = False
        return {
            'value': {'model_int_name':mod_name}
        }

    def _help_text_xsl(self, cr, context=None):
        return _("The label body can contain:\n") + \
        _("1) Fixed strings like 'Ref.:'\n") + \
        _("2) Mako fields like ${object.name} (use the expression builder to compute them)\n") + \
        _("3) Mako control sequence %%for ... %%endfor for loops\n") + \
        _("4) ReportLab tags <b> <i> <u> <super> <sub> <font> <barCode> <greek>\n") + \
        _("5) ReportLab tags like <blockTable>, <tr>, <td>, ...\n") + \
        _("6) <nextFrame/> tag where you want jump to next label.\n") + \
        _("Note: Only 1, 2, 4 contents can be mixed in the same line.\n") + \
        _("Note: Line with 1, 2, 4 content is inserted in a <para> tag.\n") + \
        _("For ReportLab documentation visit http://www.reportlab.com/software/documentation/\n")

    def _help_text_rml(self, cr, context=None):
        return _("The label body can contain:\n") + \
        _('1) Fixed strings in <para> tags like <para style="default">Ref.:</para>\n') + \
        _("2) Mako fields like ${object.name} (use the expression builder to compute them)\n") + \
        _("3) Mako control sequence %%for ... %%endfor for loops\n") + \
        _("4) ReportLab tags <b> <i> <u> <super> <sub> <font> <barCode> <greek>\n") + \
        _("5) ReportLab tags like <blockTable>, <tr>, <td>, ...\n") + \
        _("6) <nextFrame/> tag is not needed.\n") + \
        _("For Mako documentation visit http://www.makotemplates.org/docs/syntax.html\n") + \
        _("For ReportLab documentation visit http://www.reportlab.com/software/documentation/\n")

    def _help_text(self, cr, uid, ids, name, args, context=None):
        res = {}
        for tmpl in self.read(cr, uid, ids, ['type']):
            try:
                res[tmpl['id']] = getattr(self, '_help_text_' + 
tmpl['type'])(cr, context=context)
            except AttributeError:
                res[tmpl['id']] = ''
        return res

    def change_type(self, cr, uid, ids, tmpl_type, context=None):
        try:
            help_text = getattr(self, '_help_text_' + tmpl_type)(cr, context=context)
        except AttributeError:
            help_text = ''
        return {
            'value': {'help_text': help_text}
        }

    _columns = {
        'name': fields.char('Name of Template', size=100, required=True),
        'object_name': fields.many2one('ir.model', 'Model'),
        'model_int_name': fields.char('Model Internal Name', size=200,),
        'def_body_text': fields.text(
                'Label Template',
                help="""Template of one label in Mako syntax. Can contain:
1) Fixed strings like 'Ref.:'
2) Mako fields like ${object.name}
3) Mako control sequence %%for ... %%endfor for loops
4) ReportLab tags <b> <i> <u> <super> <sub> <font> <barCode> <greek>
5) ReportLab tags like <blockTable>, <tr>, <td>, ...
6) <nextFrame/> tag where you want jump to next label.
Note: Only 1, 2, 4 contents can be mixed in the same line.
Note: Line with 1, 2, 4 content is inserted in a <para> tag.
For ReportLab documentation visit http://www.reportlab.com/software/documentation/""",
                translate=True),
        'label_null': fields.char('Null for empty labels', size=256, required=True),
        'report_stylesheets': fields.text(
                'Report Style Sheets',
                help="""Optional ReportLab style sheets like:
<blockTableStyle id="mytable">
    <blockAlignment value="CENTER"/>
    <blockValign value="MIDDLE"/>
    <lineStyle kind="GRID" colorName="black" tickness="1"/>
    <blockBackground colorName="red" start="0,0" stop="0,0"/>
</blockTableStyle>"""),
        'sort_field1': fields.char(
                'Sort field 1',
                size=100,
                help="Use the same names as those of the label body "
                "definition (e.g. object.country_id.name).\n"
                "Use a slash / to concatenate a field inside a %for with "
                "the external field used to loop (e.g. object.address/o.street)."),
        'sort_field2': fields.char(
                'Sort field 2',
                size=100,
                help="Use the same names as those of the label body "
                "definition (e.g. object.country_id.name).\n"
                "Use a slash / to concatenate a field inside a %for with "
                "the external field used to loop (e.g. object.address/o.street)."),
        'sort_field3': fields.char(
                'Sort field 3',
                size=100,
                help="Use the same names as those of the label body "
                "definition (e.g. object.country_id.name).\n"
                "Use a slash / to concatenate a field inside a %for with "
                "the external field used to loop (e.g. object.address/o.street)."),
        'allowed_groups': fields.many2many(
                'res.groups',
                'label_template_group_rel',
                'templ_id', 'group_id',
                string="Allowed User Groups",
                help="Only users from these groups will be "
                "allowed to send mails from this Template."),
        'ref_ir_act_window': fields.many2one(
                'ir.actions.act_window',
                'Window Action',
                readonly=True),
        'ref_ir_value': fields.many2one(
               'ir.values',
               'Wizard Button',
               readonly=True),
        'report_template': fields.many2one(
                'ir.actions.report.xml',
                'Label Report',
                readonly=True),
        #Expression Builder fields
        #Simple Fields
        'model_object_field':fields.many2one(
                'ir.model.fields',
                string="Field",
                help="Select the field from the model you want to use."
                "\nIf it is a relationship field you will be able to "
                "choose the nested values in the box below\n(Note: If "
                "there are no values make sure you have selected the "
                "correct model).",
                store=False),
        'sub_object':fields.many2one(
                'ir.model',
                'Sub-model',
                help='When a relation field is used this field '
                'will show you the type of field you have selected.',
                store=False),
        'sub_model_object_field':fields.many2one(
                'ir.model.fields',
                'Sub Field',
                help="When you choose relationship fields "
                "this field will specify the sub value you can use.",
                store=False),
        'null_value':fields.char(
                'Null Value',
                help="This Value is used if the field is empty.",
                size=50, store=False),
        'copyvalue':fields.char(
                'Expression',
                size=100,
                help="Copy and paste the value in the "
                "location you want to use a system value.",
                store=False),
        #Table Fields
        'table_model_object_field':fields.many2one(
                'ir.model.fields',
                string="Table Field",
                help="Select the field from the model you want to use.\n"
                "(Only one2many & many2many fields can be used for tables)",
                store=False),
        'table_sub_object':fields.many2one(
                'ir.model',
                'Table-model',
                help="This field shows the model you will"
                "be using for your table.", store=False),
        'table_required_fields':fields.many2many(
                'ir.model.fields',
                'label_fields_table_rel',
                'field_id', 'table_id',
                string="Required Fields",
                help="Select the fields you require in the table.",
                store=False),
        'table_copyvalue':fields.text(
                'Table Code',
                help="Copy and paste this code to your template "
                "body for displaying the info in your label.",
                store=False),
        'type': fields.selection([
            ('xsl', 'XSL:RML'),
            ('rml', 'RML'),
            ('slcs', 'SLCS (Bixolon)'),
        ], 'Type', required=True, select=True),
        'default_label_format_id': fields.many2one('report.label',
            'Default Label Format'),
        'help_text': fields.function(_help_text, method=True,
            type='text', string='Help'),
    }

    _defaults = {
    }

    _sql_constraints = [
        ('name', 'unique (name)', _('The template name must be unique !'))
    ]

    def _report_vals_xsl(self, report_name, src_obj, oerp_full_report_name,
        full_report_name, allowed_groups):
        return {
            'name': report_name,
            'model': src_obj,
            'type': 'ir.actions.report.xml',
            'report_name': oerp_full_report_name,
            'report_xsl': 'label/custom_reports/'+full_report_name+'.xsl',
            'report_xml': '',
            'report_rml': '',
            'auto': True,
            'header': False,
            'report_type': 'pdf',
            'groups_id': allowed_groups,
        }

    def _report_vals_rml(self, report_name, src_obj, oerp_full_report_name,
        full_report_name, allowed_groups):
        return {
            'name': report_name,
            'model': src_obj,
            'type': 'ir.actions.report.xml',
            'report_name': oerp_full_report_name,
            'report_xsl': '',
            'report_xml': '',
            'report_rml': 'label/report/label_template.rml',
            'auto': False,
            'header': False,
            'report_type': 'pdf',
            'groups_id': allowed_groups,
        }

    def create_template_report(self, cr, uid, name, src_obj, allowed_groups,
        rep_type, context=None):
        """Creates template report (ir.actions.report.xml and template file)"""
        report_name = s = re.sub(r'[^-a-z0-9]+', '-', name.lower())
        full_report_name = src_obj.replace('.','_')+'_'+report_name
        oerp_full_report_name = full_report_name.replace('_','.')

        report_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=',oerp_full_report_name)], context=context)
        if report_ids:
            raise osv.except_osv(_('Error!'), _('There is another OpenERP report with the same name:\n%s\n\nChange the template name.') % oerp_full_report_name)

        # Create ir.actions.report.xml report
        try:
            report_vals = getattr(self, '_report_vals_' + rep_type)(report_name,
                src_obj, oerp_full_report_name, full_report_name, allowed_groups)
        except AttributeError:
            raise osv.except_osv(_('Warning'),
                _('You have to install the label_%s module to use this template type.') % rep_type)
        #print report_vals
        return self.pool.get('ir.actions.report.xml').create(cr, uid, report_vals, context)

    def delete_template_report(self, cr, uid, id, context=None):
        """Deletes template report (ir.actions.report.xml and template file)"""
        template = self.browse(cr, uid, id, context)
        if template.report_template:
            # Delete file if exists
            path = os.path.abspath( os.path.dirname(__file__) )
            file_out = path+'/custom_reports/%s.xsl' % template.report_template.report_name.replace('.','_')
            if os.path.isfile(file_out):
                os.remove(file_out)
            # Delete ir.actions.report.xml report
            self.pool.get('ir.actions.report.xml').unlink(cr, uid, [template.report_template.id], context)

    def create(self, cr, uid, vals, context=None):
        id = super(label_templates, self).create(cr, uid, vals, context)
        src_obj = self.pool.get('ir.model').read(cr, uid, vals['object_name'], ['model'], context)['model']

        # Create report (action + template file)
        report_template = self.create_template_report(cr, uid, vals['name'],
            src_obj, vals['allowed_groups'], vals['type'], context)

        # Create action window and wizard button
        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'label.wizard.form')], context=context)
        if len( view_id ):
            view_id = view_id[0]
        else:
            view_id = False
        ref_ir_act_window = self.pool.get('ir.actions.act_window').create(cr, uid, {
             'name': _('Label %s') % vals['name'],
             'type': 'ir.actions.act_window',
             'res_model': 'label.wizard',
             'src_model': src_obj,
             'view_type': 'form',
             'context': "{'src_model':'%s','template_id':'%d','src_rec_id':active_id,'src_rec_ids':active_ids}" % (src_obj, id),
             'view_mode':'form,tree',
             'view_id': view_id,
             'target': 'new',
             'auto_refresh':1
        }, context)
        ref_ir_value = self.pool.get('ir.values').create(cr, uid, {
             'name': _('Label %s') % vals['name'],
             'model': src_obj,
             'key2': 'client_action_multi',
             'value': "ir.actions.act_window," + str(ref_ir_act_window),
             'object': True,
         }, context)
        super(label_templates, self).write(cr, uid, id, {
            'ref_ir_act_window': ref_ir_act_window,
            'ref_ir_value': ref_ir_value,
            'report_template': report_template,
        }, context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        result = True
        for template in self.browse(cr, uid, ids, context):
            # Delete report (action + template file)
            self.delete_template_report(cr, uid, template.id, context)

            # Create report (action + template file)
            name = vals.get('name', template.name)
            object_name = vals.get('object_name', template.object_name)
            allowed_groups = vals.get('allowed_groups', [(6, 0, [r.id for r in template.allowed_groups])])
            src_obj = self.pool.get('ir.model').read(cr, uid, object_name.id, ['model'], context)['model']
            vals['report_template'] = self.create_template_report(cr, uid,
                name, src_obj, allowed_groups, vals.get('type', template.type),
                context)

            result = result and super(label_templates, self).write(cr, uid, [template.id], vals, context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        for template in self.browse(cr, uid, ids, context):
            obj = self.pool.get(template.object_name.model)

            #Delete actions
            if hasattr(obj, 'old_create'):
                obj.create = obj.old_create
                del obj.old_create
            if hasattr(obj, 'old_write'):
                obj.write = obj.old_write
                del obj.old_write
            try:
                # Delete action window and wizard button
                if template.ref_ir_act_window:
                    self.pool.get('ir.actions.act_window').unlink(cr, uid, template.ref_ir_act_window.id, context)
                if template.ref_ir_value:
                    self.pool.get('ir.values').unlink(cr, uid, template.ref_ir_value.id, context)
                # Delete report (action + template file)
                self.delete_template_report(cr, uid, template.id, context)
            except:
                raise osv.except_osv(_("Warning"), _("Deletion of Record failed"))
        return super(label_templates, self).unlink(cr, uid, ids, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        old = self.read(cr, uid, id, ['name'], context=context)
        new_name = _("Copy of template ") + old.get('name', 'No Name')
        check = self.search(cr, uid, [('name', '=', new_name)], context=context)
        if check:
            new_name = new_name + '_' + random.choice('abcdefghij') + random.choice('lmnopqrs') + random.choice('tuvwzyz')
        default.update({'name':new_name, 'partner_event_type_id': False})
        return super(label_templates, self).copy(cr, uid, id, default, context)

    def compute_pl(self,
                   model_object_field,
                   sub_model_object_field,
                   null_value, template_language='mako'):
        """
        Returns the expression based on data provided
        @param model_object_field: First level field
        @param sub_model_object_field: Second level drilled down field (M2O)
        @param null_value: What has to be returned if the value is empty
        @param template_language: The language used for templating
        @return: computed expression
        """
        #Configure for MAKO
        copy_val = ''
        if template_language == 'mako':
            if model_object_field:
                copy_val = "${object." + model_object_field
            if sub_model_object_field:
                copy_val += "." + sub_model_object_field
            if null_value:
                copy_val += " or '" + null_value + "'"
            if model_object_field:
                copy_val += "}"
        return copy_val

    def onchange_model_object_field(self, cr, uid, ids, model_object_field, context=None):
        if not model_object_field:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        #Check if field is relational
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            if res_ids:
                result['sub_object'] = res_ids[0]
                result['copyvalue'] = self.compute_pl(False,
                                                      False,
                                                      False
                                                    )
                result['sub_model_object_field'] = False
                result['null_value'] = False
        else:
            #Its a simple field... just compute placeholder
            result['sub_object'] = False
            result['copyvalue'] = self.compute_pl(field_obj.name,
                                                  False,
                                                  False
                                                  )
            result['sub_model_object_field'] = False
            result['null_value'] = False
        return {'value':result}

    def _onchange_sub_model_object_field(self, cr, uid, ids, model_object_field, sub_model_object_field, context=None):
        if not model_object_field or not sub_model_object_field:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            sub_field_obj = self.pool.get('ir.model.fields').browse(cr, uid, sub_model_object_field, context)
            if res_ids:
                result['sub_object'] = res_ids[0]
                result['copyvalue'] = self.compute_pl(field_obj.name,
                                                      sub_field_obj.name,
                                                      False
                                                      )
                result['sub_model_object_field'] = sub_model_object_field
                result['null_value'] = False
        else:
            #Its a simple field... just compute placeholder
            result['sub_object'] = False
            result['copyvalue'] = self.compute_pl(field_obj.name,
                                                  False,
                                                  False
                                                  )
            result['sub_model_object_field'] = False
            result['null_value'] = False
        return {'value':result}

    def _onchange_null_value(self, cr, uid, ids, model_object_field, sub_model_object_field, null_value, context=None):
        if not model_object_field and not null_value:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            sub_field_obj = self.pool.get('ir.model.fields').browse(cr, uid, sub_model_object_field, context)
            if res_ids:
                result['sub_object'] = res_ids[0]
                result['copyvalue'] = self.compute_pl(field_obj.name,
                                                      sub_field_obj.name,
                                                      null_value
                                                      )
                result['sub_model_object_field'] = sub_model_object_field
                result['null_value'] = null_value
        else:
            #Its a simple field... just compute placeholder
            result['sub_object'] = False
            result['copyvalue'] = self.compute_pl(field_obj.name,
                                                  False,
                                                  null_value
                                                  )
            result['sub_model_object_field'] = False
            result['null_value'] = null_value
        return {'value':result}

    def _onchange_table_model_object_field(self, cr, uid, ids, model_object_field, context=None):
        if not model_object_field:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            if res_ids:
                result['table_sub_object'] = res_ids[0]
        else:
            #Its a simple field... just compute placeholder
            result['sub_object'] = False
        return {'value':result}

    def _onchange_table_required_fields(self, cr, uid, ids, table_model_object_field, table_required_fields, template_language='mako', context=None):
        if not table_model_object_field or not table_required_fields:
            return {'value':{'table_copyvalue': False}}
        result = ''
        table_field_obj = self.pool.get('ir.model.fields').browse(cr, uid, table_model_object_field, context)
        field_obj = self.pool.get('ir.model.fields')
        #Generate mako for table
        if template_language == 'mako':
            result += "%for o in object." + table_field_obj.name + ":\n"
            for each_rec in table_required_fields[0][2]:
                result += "${o."
                record = field_obj.browse(cr, uid, each_rec, context)
                result += record.name
                result += "}\n"
            result += "%endfor\n"
        return {'value':{'table_copyvalue':result}}

    def _instantiate_report_xsl(self, template):
        label_report_engine.report_label_xsl(
            'report.' + template.report_template.report_name,
            template.report_template.model,
            '',
            'addons/' + template.report_template.report_xsl)

    def _instantiate_report_rml(self, template):
        label_report_engine.report_label_rml(
            'report.' + template.report_template.report_name,
            template.report_template.model)

    def instantiate_report(self, template):
        getattr(self, '_instantiate_report_' + template.type)(template)

label_templates()
