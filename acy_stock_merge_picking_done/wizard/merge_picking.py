# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _

class stock_picking_merge_wizard(osv.osv_memory):
    _inherit = "stock.picking.merge.wizard"
    
    def do_check(self, cr, uid, ids, context=None):
        # check if pickings are compatible again with the attributes
        # depending on additional modules!
        # I could not bring those to the domain, as there are no optional module dependencies in OpenERP for XML

        for session in self.browse(cr, uid, ids):
            target = session.target_picking_id
            for merge in session.picking_ids:
                # look for incompatible moves
                #for move in merge.move_lines:
                    #if (move.state == 'done'):
                        #raise osv.except_osv(_('Warning'),
                              #_('The following picking can not be merged due to moves in state done:') + " " + str(merge.name))
                        #return self.return_view(cr, uid, 'merge_picking_form_target', ids[0])
                    
                # test all many2one fields for compability,as we can't link to different targets from one merged object!
                # yes, we still need this, if we come from a link on stock.picking views, we don't have the first check!
                is_compatible = self.is_compatible_many2one(cr, uid, target, merge, context)
                if (not is_compatible['result']):
                    ex = _('The picking %s can not be merged due to different references:') % (str(merge.name))
                    for f in is_compatible['fields']:
                        desc = self.get_fieldname_translation(cr, uid, f, context)
                        ex += "\n" + desc + " (" + f.name + ")" 
                    raise osv.except_osv(_('Warning'), ex)
                    return self.return_view(cr, uid, 'merge_picking_form_target', ids[0])
         
        return self.return_view(cr, uid, 'merge_picking_form_checked', ids[0])
    
    def do_merge(self, cr, uid, ids, context=None):
        # bail out if checkbox not set
        for session in self.browse(cr, uid, ids):
            if not session.commit_merge: 
                raise osv.except_osv(_('Unchecked'),_('You did not check the Commit Merge checkbox.'))
                return self.return_view(cr, uid, 'merge_picking_form_checked', ids[0])

        # merge
        picking_pool = self.pool.get("stock.picking")
        fields_pool = self.pool.get("ir.model.fields")
    
        for session in self.browse(cr, uid, ids):
            target = session.target_picking_id
            
            target_changes = {"date_done": target.date_done }

            # prepare notes, esp. if not existing           
            if (target.note):
                target_changes['note'] = target.note + "\n"
            else:
                target_changes['note'] = ""

            if (target.merge_notes):
                target_changes['merge_notes'] = target.merge_notes + ";\n"
            else:
                target_changes['merge_notes'] = ""
            target_changes['merge_notes'] += "This is a merge target."


            for merge in session.picking_ids:
                # fetch notes

                linenote = " Merged " + str(merge.name)
                if (merge.origin != target.origin):
                    linenote += ", had Origin " + str(merge.origin)
                
                if (merge.date != target.date):
                    linenote += ", from " + str(merge.date)

                if (merge.note):
                    linenote += ", Notes: " + str(merge.note)

                target_changes['merge_notes'] += linenote + ";\n"

                if (merge.note):
                    target_changes['note'] += str(merge.note) + "\n"

                # handle changeable values

                # if any one merge has partial delivery, deliver the whole picking as partial (direct)
                if (merge.move_type == 'direct'):
                    target_changes['move_type'] = 'direct'
                
                # date_done = MAX(date_done)
                if (target_changes['date_done'] < merge.date_done):
                    target_changes['date_done'] = merge.date_done
                
                # if any one merge is NOT auto_picking, then the target is not.
                # should never occur, as auto_picking would set it to done instantly, which can't be merged
                if (not (merge.auto_picking)):
                    target_changes['auto_picking'] = False
                
                # search for all outgoing related fields.
                # we handle only ougoing many2one (incoming one2many may not exist for that) here
                # this IS neccessary, but only to catch specialhandler-handled fields.
                # must be done before the next search, because refs might have been destroyed later
                fields_search = fields_pool.search(cr, uid, [('model','=','stock.picking'),('ttype','=','many2one')])
                                
                # go through these fields
                for field in fields_pool.browse(cr, uid, fields_search):
                    
                    if field.name in self.get_specialhandlers().keys():
                        # use special handler
                        specialhandler_name = self.get_specialhandlers().get(field.name)
                        specialhandler = getattr(self, specialhandler_name)
                        target_changes = specialhandler(cr, uid, field.name, merge, target, target_changes)

                
                # search for all incoming related fields.
                # we don't need to handle one2many here: would be backlinked versions of many2one anyway.
                fields_search = fields_pool.search(cr, uid, [('relation','=','stock.picking'),('model','<>',self._name),
                                                             '|',('ttype','=','many2one'),('ttype','=','many2many')])
                
                # go through these fields
                for field in fields_pool.browse(cr, uid, fields_search):
                    
                    if field.name in self.get_specialhandlers().keys():
                        # use special handler
                        specialhandler_name = self.get_specialhandlers().get(field.name)
                        specialhandler = getattr(self, specialhandler_name)
                        target_changes = specialhandler(cr, uid, field.name, merge, target, target_changes)

                        
                ## update all relations to the old picking to look for the new one
                ## includes stock.move lines merge


                # go through these fields and change things, using field_search from before (many2one | many2many)
                for field in fields_pool.browse(cr, uid, fields_search):


                    if not (field.name in self.get_specialhandlers().keys()):
                        # find the model they're in
                        model_pool = self.pool.get(field.model)

                        # this can happen if you deinstalled modules by deleting their code, so they left something behind in the definition.
                        if (not model_pool):
                            continue

                        # do not handle relations to views
                        if self.is_view(model_pool):
                            continue
                        
                        # handle many2one: simply replace the id 
                        if (field.ttype == 'many2one'):
                            # find all entries that are old
                            model_search = model_pool.search(cr, uid, [(field.name,'=',merge.id)])
                            # and update them in one go
                            model_pool.write(cr, uid, model_search, {field.name: target.id})
    
                        # handle many2many:  
                        if (field.ttype == 'many2many'):
                            # find all entries that are old (don't know how yet, so I'll have to take 'em all
                            model_search = model_pool.search(cr, uid, []) # (field.name,'=',merge.id)
                            # and update them in one go
                            model_pool.write(cr, uid, model_search, {field.name: [(3,merge.id),(4,target.id)]})
                        
                        
                
                        
                # updated everything, so now I can get rid of the object
                picking_pool.write(cr,uid,[merge.id],{'state':'draft'})
                picking_pool.unlink(cr, uid, [merge.id])

            # /for merge
            picking_pool.write(cr, uid, [target.id], target_changes)
                
        return self.return_view(cr, uid, 'merge_picking_form_done', ids[0])
    
stock_picking_merge_wizard()