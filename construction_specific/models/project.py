from openerp.osv import fields, osv

class Task(osv.osv):
    _inherit = 'project.task'

    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        stage_obj = self.pool.get('project.task.type')
        order = stage_obj._order
        access_rights_uid = access_rights_uid or uid
        if read_group_order == 'stage_id desc':
            order = '%s desc' % order
        search_domain = []
        project_id = self._resolve_project_id_from_context(cr, uid, context=context)
        if project_id:
            search_domain += ['|', ('project_ids', '=', project_id)]
        search_domain += [('id', 'in', ids)]
        stage_ids = stage_obj._search(cr, uid, [], order=order, access_rights_uid=access_rights_uid, context=context)
        result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)
        # restore order of the search
        result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

        fold = {}
        for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
            fold[stage.id] = stage.fold or False
        return result, fold

    def _read_group_user_id(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res_users = self.pool.get('res.users')
        project_id = self._resolve_project_id_from_context(cr, uid, context=context)
        access_rights_uid = access_rights_uid or uid
        if project_id:
            ids += self.pool.get('project.project').read(cr, access_rights_uid, project_id, ['members'], context=context)['members']
            order = res_users._order
            # lame way to allow reverting search, should just work in the trivial case
            if read_group_order == 'user_id desc':
                order = '%s desc' % order
            # de-duplicate and apply search order
            ids = res_users._search(cr, uid, [('id','in',ids)], order=order, access_rights_uid=access_rights_uid, context=context)
        result = res_users.name_get(cr, access_rights_uid, ids, context=context)
        # restore order of the search
        result.sort(lambda x,y: cmp(ids.index(x[0]), ids.index(y[0])))
        return result, {}

    _group_by_full = {
        'stage_id': _read_group_stage_ids,
        'user_id': _read_group_user_id,
    }
