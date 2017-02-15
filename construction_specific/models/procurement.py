from openerp.osv import fields, osv

class procurement_order(osv.osv):
    _inherit = "procurement.order"

    def _is_procurement_task(self, cr, uid, procurement, context=None):
        is_proc_task = super(procurement_order, self)._is_procurement_task(
            cr, uid, procurement, context)
        if procurement.product_id.type == 'consu' and procurement.product_id.auto_create_task:
            is_proc_task = True
        return is_proc_task
    
    def _convert_qty_company_hours(self, cr, uid, procurement, context=None):
        product_uom = self.pool.get('product.uom')
        company_time_uom_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.project_time_mode_id
        if procurement.product_uom.id != company_time_uom_id.id and procurement.product_uom.category_id.id == company_time_uom_id.category_id.id:
            planned_hours = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.sale_line_id.line_human, company_time_uom_id.id)
        else:
            planned_hours = procurement.sale_line_id.line_human
        return planned_hours
