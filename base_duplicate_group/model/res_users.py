from openerp.osv import fields, osv, expression

class res_groups(osv.osv):
    _inherit = "res.groups"
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        login = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({'name': login+' (copy)'})
        return super(res_groups, self).copy(cr, uid, id, default, context)