


from openerp.osv import fields, osv
from openerp import api

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _credit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'receivable', args, context=context)

    def _debit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'payable', args, context=context)
    
    def _credit_debit_get(self, cr, uid, ids, field_names, arg, context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=ctx)
        model_id = self.pool.get('ir.model').search(cr, uid, [('model','=','account.move.line')])[0]
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        groups_ids = [group.id for group in user.groups_id]
        rule_id = self.pool.get('ir.rule').search(cr, uid,
                                               [('global','=',False),
                                                ('domain_force','like',str(uid)),
                                                ('model_id','=',model_id),
                                                ('groups','in',groups_ids)])
        if rule_id and len(rule_id) == 1:
            rule = self.pool.get('ir.rule').browse(cr, uid, rule_id, context)
            user_ids = eval(rule.domain_force)[0][2]
                
            cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                          FROM account_move_line l
                          LEFT JOIN account_account a ON (l.account_id=a.id)
                          WHERE a.type IN ('receivable','payable')
                          AND l.partner_id IN %s
                          AND l.reconcile_id IS NULL
                          AND l.create_uid IN %s
                          AND """ + query + """
                          GROUP BY l.partner_id, a.type
                          """,
                       (tuple(ids),tuple(user_ids),))
        else:
            cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                          FROM account_move_line l
                          LEFT JOIN account_account a ON (l.account_id=a.id)
                          WHERE a.type IN ('receivable','payable')
                          AND l.partner_id IN %s
                          AND l.reconcile_id IS NULL
                          AND """ + query + """
                          GROUP BY l.partner_id, a.type
                          """,
                       (tuple(ids),))
        maps = {'receivable':'credit', 'payable':'debit' }
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for pid,type,val in cr.fetchall():
            if val is None: val=0
            res[pid][maps[type]] = (type=='receivable') and val or -val
        return res
    
    _columns = {
        'credit': fields.function(
            _credit_debit_get, fnct_search=_credit_search,
            string='Total Receivable', multi='dc',
            help="Total amount this customer owes you."),
        'debit': fields.function(
            _credit_debit_get, fnct_search=_debit_search,
            string='Total Payable', multi='dc',
            help="Total amount you have to pay to this supplier."),
    }