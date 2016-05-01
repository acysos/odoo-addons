# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class mrp_autocontrol(osv.osv):
    _name='mrp.autocontrol'
    _description = 'Product Autocontrols'
    
    _columns = {
        'sequence': fields.integer('Sequence',required=True),
        'name': fields.char('Name', required=True, size=128, translate=True),
        'tolerance': fields.char('Tolerance', size=128, translate=True),
        'frecuency': fields.char('Frecuency', size=128, translate=True),
        'tools': fields.char('Tools', size=128, translate=True),
        'mrp_id': fields.many2one('mrp.production', 'MRP', ondelete='cascade'),
    }
    
    _order = 'sequence'
    
#     _sql_constraints = [
#         ('sequence_product_uniq', 'unique (sequence,product_id)', 'The sequence must be unique per product !')
#     ]


'''class registry_autocontrol_line(osv.osv):
    _name = 'registry.autocontrol.line'
    _description = 'Registry Autocontrol Line'

    _columns = {
            'sequence': fields.integer('Sequence',required=True),
            'name': fields.char('Name', required=True, size=128, translate=True),
            'tools': fields.char('Tools', size=128, translate=True),
            'type':fields.selection([
                    ('boolean','Boolean'),
                    ('number','Number'),
                    ],'Type'),
            'res_boolean':fields.boolean('Boolean'),
            'res_min_margin': fields.integer('Min. Margin'),
            'res_max_margin': fields.integer('Max. Margin'),
            'registry_id': fields.many2one('registry.autocontrol', 'Autocontrol Registry', ondelete='cascade'),
            'mrp_id': fields.many2one('mrp.production', 'MRP', ondelete='cascade'),
            'state_type': fields.selection([
                       ('start','Start'),
                       ('intermediate','Intermediate'),
                       ('final','Final')
             ],'State Type'),
        }
registry_autocontrol_line()

class registry_autocontrol(osv.osv):
    _name = 'registry.autocontrol'
    _description = 'Registry Autocontrol'

    _columns = {
            'name':fields.char('Reference', size=255, required=False, readonly=True),
            'mrp_id': fields.many2one('mrp.production', 'Manufacturing Order', ondelete='cascade'),
            'product_id': fields.many2one('product.product', 'Product', ondelete='cascade'),
            'state': fields.selection([
                       ('start','Start'),
                       ('intermediate','Intermediate'),
                       ('final','Final')
                       ],'State', readonly=True),
            'start_autocontrol_ids': fields.one2many('registry.autocontrol.line', 
                     'registry_id', 
                     'Start Product Autocontrols',
                     states={'intermediate':[('readonly',True)], 'final':[('readonly',True)]}),
            'intermediate_autocontrol_ids': fields.one2many('registry.autocontrol.line', 
                    'registry_id', 
                    'Intermediate Product Autocontrols',
                     states={'start':[('readonly',True)], 'final':[('readonly',True)]}),
            'final_autocontrol_ids': fields.one2many('registry.autocontrol.line', 
                     'registry_id', 
                     'Final Product Autocontrols',
                     states={'intermediate':[('readonly',True)], 'start':[('readonly',True)]}),
            'date': fields.date('Date'),
        }
    
    _defaults = {  
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'start', 
    }
    
registry_autocontrol()'''

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    _columns = {
        'autocontrol_ids': fields.one2many('mrp.autocontrol', 'mrp_id', 'Product Autocontrols',readonly=True),
    }
    
    def action_compute(self, cr, uid, ids, properties=[], context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        results = []
        bom_obj = self.pool.get('mrp.bom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_autocontrol where mrp_id=%s', (production.id,))
            #cr.execute('delete from registry_autocontrol_line where mrp_id=%s', (production.id,))
            #cr.execute('delete from registry_autocontrol where mrp_id=%s', (production.id,))
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error'), _("Couldn't find bill of material for product"))

            mrp_autocontrol_obj = self.pool.get('mrp.autocontrol')
            #reg_control_line_obj = self.pool.get('registry.autocontrol.line')
            #registry_id = self.pool.get('registry.autocontrol').create(cr,uid,{
            #        'name': 'ACR'+production.name,
            #        'mrp_id': production.id
            #    })
            for control in reversed(production.product_id.autocontrol_id):
                if control.tolerance == False:
                    control.tolerance = ''
                if control.frecuency == False:
                    control.frecuency = ''
                if control.tools == False:
                    control.tools = ''
                mrp_autocontrol_obj.create(cr,uid,{
                       'sequence':control.sequence,
                       'name':control.name,
                       'tolerance':control.tolerance,
                       'frecuency':control.frecuency,
                       'tools':control.tools,
                       'mrp_id': production.id
                   })
                values_reg_lines = {
                        'sequence':control.sequence,
                        'name':control.name,
                        'tools':control.tools,
                    }
                #reg_control_line_obj.create(cr,uid,values)

            factor = production.product_qty * production.product_uom.factor_inv / bom_point.product_uom.factor
            res = bom_obj._bom_explode(cr, uid, bom_point, production.product_id, factor / bom_point.product_qty, properties)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)

