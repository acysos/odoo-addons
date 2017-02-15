from openerp import models, fields, api


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    @api.one
    def _get_hr_line(self):
        hr_sheet = self.env['hr.analytic.timesheet']
        self.hr_line = hr_sheet.search([('line_id', '=', self.id)])

    @api.one
    @api.depends('hr_line')
    def _get_worked_rate(self):
        self.worked_rate = self.hr_line.worked_rate.id or None

    @api.multi
    def _get_supplier(self):
        pur_line_obj = self.env['purchase.order.line']
        for line in self:
            pur_line = pur_line_obj.search([('analytic_line', '=', line.id)])
            line.supplier = pur_line.partner_id.id

    @api.multi
    def _get_supplier_ref(self):
        pur_line_obj = self.env['purchase.order.line']
        for line in self:
            pur_line = pur_line_obj.search([('analytic_line', '=', line.id)])
            line.supplier_ref = pur_line.order_id.partner_ref

    hr_line = fields.Many2one(string="Tipo de hora",
                              comodel_name='hr.analytic.timesheet',
                              compute="_get_hr_line")
    worked_rate = fields.Many2one(string="Tipo de hora",
                                  comodel_name='hr.payslip.worker.rate',
                                  compute="_get_worked_rate", store=True)
    supplier = fields.Many2one(string="Proveedor", comodel_name='res.partner',
                               compute='_get_supplier')
    supplier_ref = fields.Char(string="Ref. Proveedor", 
                               compute='_get_supplier_ref')
