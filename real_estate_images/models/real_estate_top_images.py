# -*- coding: utf-8 -*-
# © 2017 Acysos S.L. Daniel Pascal <daniel@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class RealEstateTop(models.Model):
    _name = 'real.estate.top'
    _inherit = [_name, "base_multi_image.owner"]

    # Make this field computed for getting only the available images
    
    image_main = fields.Binary(inverse="_inverse_main_image_large")
    image_main_medium = fields.Binary(inverse="_inverse_main_image_medium")
    image_main_small = fields.Binary(inverse="_inverse_main_image_small")
    
    def launch_wizard(self):
        context = self.env.context.copy()
        context['active_ids'] = self.ids
        wizard_model = 'multimages.wizard'
        return {
            'name': _('Add Images to the Top'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wizard_model,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            }
    

    def _inverse_main_image(self, image):
        for top in self:
            if image:
                top.image_ids[0].write({
                    'file_db_store': image,
                    'storage': 'db',
                })
            else:
                top.image_ids = [(3, top.image_ids[0].id)]
                
    def _inverse_main_image_large(self):
        for top in self:
            top._inverse_main_image(top.image_main)

    def _inverse_main_image_medium(self):
        for top in self:
            top._inverse_main_image(top.image_main_medium)

    def _inverse_main_image_small(self):
        for top in self:
            top._inverse_main_image(top.image_main_small)


