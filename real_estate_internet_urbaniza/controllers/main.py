# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#                       Daniel Pascal <daniel@acysos.com>
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

import werkzeug.urls
import base64
import urllib2
from werkzeug.exceptions import NotFound

from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.tools import ustr

def content_disposition(filename):
    filename = ustr(filename)
    escaped = urllib2.quote(filename.encode('utf8'))
    browser = request.httprequest.user_agent.browser
    version = int((request.httprequest.user_agent.version or '0').split('.')[0])
    if browser == 'msie' and version < 9:
        return "attachment; filename=%s" % escaped
    elif browser == 'safari' and version < 537:
        return u"attachment; filename=%s" % filename.encode('ascii', 'replace')
    else:
        return "attachment; filename*=UTF-8''%s" % escaped

class idealista_event(http.Controller):
    @http.route(['/realestateportal/urbaniza.xml'], type='http', auth="public", website=True)
    
    def event_register(self, **post):
        xml = request.env['real.estate.top'].xml_inmoagrupacom()
        values = {
            'xml': xml
        }

        return request.render(
            "real_estate_internet_urbaniza.inmoagrupacom_template",
            values, mimetype='application/xml;charset=utf-8')
        
    @http.route([
        '/website/image/<model>/<id>/<field>/image.jpg',
        '/website/image/<model>/<id>/<field>/image.JPG',
        '/website/image/<model>/<id>/<field>/image.gif',
        '/website/image/<model>/<id>/<field>/image.GIF',
        '/website/image/<model>/<id>/<field>/image.png',
        '/website/image/<model>/<id>/<field>/image.PNG'
        ], auth="public", website=True, multilang=False)
    def website_image(self, model, id, field, max_width=None, max_height=None):
        """ Fetches the requested field and ensures it does not go above
        (max_width, max_height), resizing it if necessary.

        If the record is not found or does not have the requested field,
        returns a placeholder image via :meth:`~.placeholder`.

        Sets and checks conditional response parameters:
        * :mailheader:`ETag` is always set (and checked)
        * :mailheader:`Last-Modified is set iif the record has a concurrency
          field (``__last_update``)

        The requested field is assumed to be base64-encoded image data in
        all cases.
        """
        try:
            idsha = id.split('_')
            id = idsha[0]
            response = werkzeug.wrappers.Response()
            return request.registry['website']._image(
                request.cr, request.uid, model, id, field, response, max_width, max_height,
                cache=STATIC_CACHE if len(idsha) > 1 else None)
        except Exception:
            logger.exception("Cannot render image field %r of record %s[%s] at size(%s,%s)",
                             field, model, id, max_width, max_height)
            response = werkzeug.wrappers.Response()
            return self.placeholder(response)

    @http.route([
        '/website/pdf/<model>/<field>/<id>/<filename_field>/pdf.pdf',
        '/website/pdf/<model>/<field>/<id>/<filename_field>/pdf.PDF'
        ], auth="public", website=True, multilang=False)
    def saveas(self, model, field, id=None, filename_field=None, **kw):
        """ Download link for files stored as binary fields.

        If the ``id`` parameter is omitted, fetches the default value for the
        binary field (via ``default_get``), otherwise fetches the field for
        that precise record.

        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename_field: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context
        fields = [field]
        content_type = 'application/octet-stream'
        if filename_field:
            fields.append(filename_field)
        if id:
            fields.append('file_type')
            res = Model.read(cr, uid, [int(id)], fields, context)[0]
            if res.get('file_type'):
                content_type = res['file_type']
        else:
            res = Model.default_get(cr, uid, fields, context)
        filecontent = base64.b64decode(res.get(field) or '')
        if not filecontent:
            return request.not_found()
        else:
            filename = '%s_%s' % (model.replace('.', '_'), id)
            if filename_field:
                filename = res.get(filename_field, '') or filename
            return request.make_response(
                filecontent, [('Content-Type', content_type),
                              ('Content-Disposition',
                               content_disposition(filename))])



    