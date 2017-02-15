from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _get_purchase_ref(self):
        for picking in self:
            if picking.move_lines[0].purchase_line_id.order_id:
                purchase = picking.move_lines[0].purchase_line_id.order_id
                picking.purchase_ref = purchase.partner_ref

    sale_ref = fields.Char(string='Ref. Venta',
                           related='sale_id.client_order_ref')
    purchase_ref = fields.Char(string='Ref. Compra',
                               compute='_get_purchase_ref')
#     task_name = fields.Char(string='Nombre tarea',
#                             related='sale_id.task_name')
    user_id = fields.Many2one(string='Comercial', related='sale_id.user_id')

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(StockPicking, self)._get_invoice_vals(key, inv_type,
                                                          journal_id, move)
        res['comment'] = ''
        return res
    
    def action_invoice_create(self, cr, uid, ids, journal_id, group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        context = context or {}
        todo = {}
        for picking in self.browse(cr, uid, ids, context=context):
            partner = picking.partner_id.id
            #grouping is based on the invoiced partner
            if group:
                key = partner
            else:
                key = picking.id
            for move in picking.move_lines:
                if move.invoice_state == '2binvoiced':
                    if (move.state != 'cancel'):
                        todo.setdefault(key, [])
                        todo[key].append(move)
        invoices = []
        for moves in todo.values():
            invoices += self._invoice_create_line(cr, uid, moves, journal_id, type, context=context)
        return invoices
    
    def _invoice_create_line(self, cr, uid, moves, journal_id, inv_type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('stock.move')
        invoices = {}
        for move in moves:
            company = move.company_id
            origin = move.picking_id.name
            partner, user_id, currency_id = move_obj._get_master_data(cr, uid, move, company, context=context)

            key = (partner, currency_id, company.id, 1)
            invoice_vals = self._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
            if key not in invoices:
                # Get account and payment terms
                invoice_id = self._create_invoice_from_picking(cr, uid, move.picking_id, invoice_vals, context=context)
                invoices[key] = invoice_id
            else:
                invoice = invoice_obj.browse(cr, uid, invoices[key], context=context)
                if not invoice.origin or invoice_vals['origin'] not in invoice.origin.split(', '):
                    invoice_origin = filter(None, [invoice.origin, invoice_vals['origin']])
                    invoice.write({'origin': ', '.join(invoice_origin)})

            invoice_line_vals = move_obj._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
            invoice_line_vals['invoice_id'] = invoices[key]
            invoice_line_vals['origin'] = origin

            move_obj._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)
            move_obj.write(cr, uid, move.id, {'invoice_state': 'invoiced'}, context=context)

        invoice_obj.button_compute(cr, uid, invoices.values(), context=context, set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoices.values()


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move, partner,
                                                            inv_type)
        name = ''
        if inv_type == 'out_invoice' and move.picking_id.sale_id:
            if move.picking_id.sale_id.client_order_ref:
                name += ' [' + move.picking_id.sale_id.client_order_ref + ']'
        name += '[' + move.picking_id.name + '] '
        if inv_type == 'in_invoice' and move.purchase_line_id:
            if move.purchase_line_id.order_id.partner_ref:
                name += ' [' + move.purchase_line_id.order_id.partner_ref + ']'
        name += '\n' + move.name
        res['name'] = name
        return res
