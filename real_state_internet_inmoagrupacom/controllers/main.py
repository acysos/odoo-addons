# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

import werkzeug.urls
from werkzeug.exceptions import NotFound

from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

class idealista_event(http.Controller):
    @http.route(['/realstateportal/inmoagrupacom.xml'], type='http', auth="public", website=True)
    
    def event_register(self, **post):
        xml = request.env['real.state.top'].xml_inmoagrupacom()
        values = {
            'xml': xml
        }
        return request.render("real_state_internet_inmoagrupacom.inmoagrupacom_template",values, mimetype='application/xml;charset=utf-8')
        


    