from openerp.osv import fields, osv

class account_chart(osv.osv_memory):
    _inherit = "account.chart"

    def account_chart_open_window(self, cr, uid, ids, context=None):
        print "Ok"
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        period_obj = self.pool.get('account.period')
        fy_obj = self.pool.get('account.fiscalyear')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_account_tree')
        print "Result 1"
        print result
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        print "Result 2"
        print result
        fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
        result['periods'] = []
        if data['period_from'] and data['period_to']:
            period_from = data.get('period_from', False) and data['period_from'][0] or False
            period_to = data.get('period_to', False) and data['period_to'][0] or False
            result['periods'] = period_obj.build_ctx_periods(cr, uid, period_from, period_to)
        result['context'] = str({'fiscalyear': fiscalyear_id, 'periods': result['periods'], \
                                    'state': data['target_move'], 'uid': uid})
        if fiscalyear_id:
            result['name'] += ':' + fy_obj.read(cr, uid, [fiscalyear_id], context=context)[0]['code']
        print "Result 3"
        print result
        return result