from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = super(sale_order, self)._amount_all(cr, uid, ids, field_name,
                                                  arg, context)
        res2 = {}
        for key, value in res.iteritems():
            bi = value['amount_untaxed'] - self.browse(cr, uid, key, context).sale_costs
            if value['amount_untaxed'] != 0:
                per_bi = (bi / value['amount_untaxed']) * 100
            else:
                per_bi = 0
            value['industrial_profit'] = bi
            value['percentage_ip'] = per_bi
            res2[key] = value
        return res2

    def _get_order(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('sale.order.line')
        return list(set(line['order_id'] for line in line_obj.read(
            cr, uid, ids, ['order_id'], load='_classic_write', context=context)))

    _columns = {
        'industrial_profit': fields.function(
            _amount_all_wrapper,
            digits_compute=dp.get_precision('Account'), string='BI',
#             store={
#                 'sale.order': (lambda self, cr, uid, ids, c={}: ids,
#                                ['order_line'], 10),
#                 'sale.order.line': (_get_order,
#                                     ['price_unit', 'tax_id', 'discount',
#                                      'product_uom_qty'], 10),
#             },
            multi='sums', help="Beneficio Industrial",
            track_visibility='always'),
        'percentage_ip': fields.function(
            _amount_all_wrapper,
            digits_compute=dp.get_precision('Account'), string='% BI',
#             store={
#                 'sale.order': (lambda self, cr, uid, ids, c={}: ids,
#                                ['order_line'], 10),
#                 'sale.order.line': (_get_order,
#                                     ['price_unit', 'tax_id', 'discount',
#                                      'product_uom_qty'], 10),
#             },
            multi='sums', help="Porcentaje beneficio industrial",
            track_visibility='always'),
        'order_line': fields.one2many('sale.order.line', 'order_id',
                                      'Order Lines', copy=True),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('invoiced', 'Facturado'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
    }

    def action_ship_create(self, cr, uid, ids, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """
        context = context or {}
        context['lang'] = self.pool['res.users'].browse(cr, uid, uid).lang
        procurement_obj = self.pool.get('procurement.order')
        sale_line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []
            vals = self._prepare_procurement_group(cr, uid, order, context=context)
            if not order.procurement_group_id:
                group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                order.write({'procurement_group_id': group_id})

            for line in order.order_line:
                if line.state == 'cancel':
                    continue
                #Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
                if line.procurement_ids:
                    #first check them to see if they are in exception or not (one of the related moves is cancelled)
                    procurement_obj.check(cr, uid, [x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
                    line.refresh()
                    #run again procurement that are in exception in order to trigger another move
                    except_proc_ids = [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
                    procurement_obj.reset_to_confirmed(cr, uid, except_proc_ids, context=context)
                    proc_ids += except_proc_ids
                elif sale_line_obj.need_procurement(cr, uid, [line.id], context=context):
                    if (line.state == 'done') or not line.product_id:
                        continue
                    vals = self._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=context)
                    ctx = context.copy()
                    ctx['procurement_autorun_defer'] = True
                    proc_id = procurement_obj.create(cr, uid, vals, context=ctx)
                    proc_ids.append(proc_id)
            #Confirm procurement order such that rules will be applied on it
            #note that the workflow normally ensure proc_ids isn't an empty list
            procurement_obj.run(cr, uid, proc_ids, context=context)
            
            # Fix Sale Line One Task. TODO locete real problem
            line_obj = self.pool.get('sale.order.line')
            for procurement in procurement_obj.browse(cr, uid, proc_ids, context):
                line_id = line_obj.search(cr, uid, [('order_id','=',procurement.sale_line_id.order_id.id),('name','=',procurement.name)])
                procurement.sale_line_id = line_id[0]

            #if shipping was in exception and the user choose to recreate the delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)
        return True


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'price_unit': fields.float('Unit Price', required=True,
                                   digits_compute= dp.get_precision('Product Price')),
    }
