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

from osv import osv, fields

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
    
    _sql_constraints = [
        ('sequence_product_uniq', 'unique (sequence,product_id)', 'The sequence must be unique per product !')
    ]
    
mrp_autocontrol()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    _columns = {
        'autocontrol_ids': fields.one2many('mrp.autocontrol', 'mrp_id', 'Product Autocontrols',readonly=True),
    }
    
    def action_compute(self, cr, uid, ids, properties=[]):
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

            for control in reversed(production.product_id.autocontrol_id):
                if control.tolerance == False:
                    control.tolerance = ''
                if control.frecuency == False:
                    control.frecuency = ''
                if control.tools == False:
                    control.tools = ''
                sql = "INSERT INTO mrp_autocontrol (sequence,name,tolerance,frecuency,tools,mrp_id) VALUES (%i,'%s','%s','%s','%s',%i)" % (control.sequence,control.name,control.tolerance,control.frecuency,control.tools,production.id)
                cr.execute(sql)

            factor = production.product_qty * production.product_uom.factor_inv / bom_point.product_uom.factor
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)

    
mrp_production()