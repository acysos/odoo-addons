# -*- coding: utf-8 -*-
# © 2013 Ignacio Ibeas <ignacio@acysos.com>
# © 2017 Daniel Pascal <daniel@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import zipfile
import base64
import os
import tempfile


class MultimagesWizard(models.TransientModel):
    _name = 'multimages.wizard'

    def _default_event(self):
        return self.env['real.state.top'].browse(self._context.get('active_id'))
    
    top_id = fields.Many2one(string='topid', comodel_name='real.state.top',
                               default=_default_event)
    
    zip_tops_images = fields.Binary('Upload a zip file with images')

    @api.multi
    def add_pics(self):
        ziptodecompress = base64.decodestring(self.zip_tops_images)
        fobj = tempfile.NamedTemporaryFile(delete=False)
        fname = fobj.name
        fobj.write(ziptodecompress)
        fobj.close()
        try:
            file_object  = open(fname, 'rw')
            myzipfile = zipfile.ZipFile(file_object)
            for name in myzipfile.namelist():
                zippy = myzipfile.open(name)
                image_string = zippy.read()
                self.env['base_multi_image.image'].create({
                    'owner_id':self.top_id.id,'owner_model':'real.state.top',
                    'storage':'db', 'name': str(name), 'extension': os.path.splitext(name)[1], 
                    'file_db_store': base64.b64encode(image_string)})
        finally:
            # delete the file when done
            os.unlink(fname)
