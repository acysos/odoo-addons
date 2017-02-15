from openerp import models, fields, api
from openerp.osv.fields import related


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'id desc'

    @api.one
    @api.onchange('order_line')
    def _get_total_human(self):
        self.total_human = 0
        for order in self:
            for line in order.order_line:
                self.total_human += line.line_human

    @api.one
    @api.onchange('order_line')
    def _get_total_material(self):
        self.total_material = 0
        for order in self:
            for line in order.order_line:
                self.total_material += line.line_material

    @api.one
    @api.onchange('total_human', 'total_material')
    def _get_total_cost(self):
        self.sale_costs = 0
        for order in self:
            order.sale_costs += order.total_human * \
                self.env.user.company_id.human_cost + order.total_material

    @api.one
    def button_calculate_totals(self):
        self._get_total_cost()
        self._get_total_human()
        self._get_total_material()
        self._get_bi()
        self._get_per_bi()

    @api.multi
    def _get_date_shipped(self):
        for order in self:
            date = None
            for picking in order.picking_ids:
                if date is None or date < picking.date_done:
                    date = picking.date_done
            order.date_shipped = date

    @api.one
    @api.onchange('amount_untaxed')
    def _get_bi(self):
        self.industrial_profit = self.amount_untaxed - self.sale_costs

    @api.one
    @api.onchange('amount_untaxed')
    def _get_per_bi(self):
        if self.amount_untaxed != 0:
            self.percentage_ip = (self.industrial_profit /
                                  self.amount_untaxed) * 100
        else:
            self.percentage_ip = 0

    @api.model
    def _prepare_project_vals(self, order):
        vals = super(SaleOrder, self)._prepare_project_vals(order)
#         vals['name'] = u" %s - %s - %s" % (
#             order.name,
#             order.partner_id.comercial,
#             order.task_name)
        vals['name'] = u" %s - %s" % (
            order.name,
            order.partner_id.comercial)
        return vals

    @api.multi
    def _get_project_state(self):
        for sale in self:
            state = 'Finalizado'
            if len(sale.related_project_id.tasks) > 0:
                for task in sale.related_project_id.tasks:
                    if task.stage_id.id != 7:
                        state = 'En progreso'
            else:
                state = ''
            sale.project_state = state

    @api.multi
    def _get_state2(self):
        for sale in self:
            if sale.state == 'done':
                if sale.invoiced:
                    sale.state2 = 'Pagado'
                else:
                    sale.state2 = 'Facturado'
            if sale.state == 'progress':
                if sale.invoice_exists:
                    if sale.invoiced:
                        sale.state2 = 'Pagado'
                    else:
                        sale.state2 = 'Facturado'
                else:
                    sale.state2 = 'Curso'
            if sale.state == 'draft':
                sale.state2 = 'Presupuesto borrador'
            if sale.state == 'sent':
                sale.state2 = 'Presupuesto enviado'
            if sale.state == 'cancel':
                sale.state2 = 'Cancelado'
            if sale.state == 'waiting_date':
                sale.state2 = 'Esperando fecha planificada'
            if sale.state == 'manual':
                sale.state2 = 'Venta a facturar'
            if sale.state == 'shipping_except':
                sale.state2 = 'Excepcion de envio'
            if sale.state == 'invoice_except':
                sale.state2 = 'Excepcion de factura'

    sale_costs = fields.Float(string='Coste total')
    total_human = fields.Float(string='Total Mano de obra')
    total_material = fields.Float(string='Total Materiales')
    date_estimated = fields.Datetime(string="Fecha requerida")
    date_shipped = fields.Datetime(string="Fecha entregado",
                                   compute=_get_date_shipped)
    analytic_balance = fields.Float(
        string='Coste/Beneficio',
        related='related_project_id.analytic_account_id.balance')
    project_state = fields.Char(string="Estado", compute=_get_project_state)
    state2 = fields.Char(string="Estado", compute=_get_state2)
    sale_admin = fields.Boolean(string="Pedido de administracion")

    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        print res.amount_total
        if res.amount_total == 0:
            res.sale_admin = True
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('line_human', 'line_material')
    def _get_line_cost(self):
        self.line_costs = self.line_human * \
            self.env.user.company_id.human_cost + self.line_material

    line_human = fields.Float(string='Mano de obra')
    line_material = fields.Float(string='Materiales')
    line_costs = fields.Float(string='Costes')
