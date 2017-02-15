from openerp import models, fields, api


class ProjectTaskMaterials(models.Model):
    _inherit = 'project.task.materials'

    @api.multi
    @api.onchange('product_id')
    def _change_product_id(self):
        for material in self:
            material.name = material.product_id.name
            material.standard_price = material.product_id.standard_price

    @api.multi
    @api.onchange('standard_price', 'quantity')
    def _change_subtotal(self):
        for material in self:
            material.subtotal = material.quantity * material.standard_price

    standard_price = fields.Float(string='Precio Unitario')
    name = fields.Char(string='Descripcion')
    subtotal = fields.Float(string='Subtotal')

    def _prepare_analytic_line(self):
        res = super(ProjectTaskMaterials, self)._prepare_analytic_line()
        res['amount'] -= self.subtotal
        return res
