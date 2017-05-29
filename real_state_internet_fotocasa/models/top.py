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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class real_state_top(models.Model):
    _inherit = 'real.state.top'
    
    @api.multi
    @api.onchange('fotocasa')
    def onchange_fotocasa(self):
        fotocasa_tops = self.search([('fotocasa','=',True),
                                    ('available','=',True)])
        
        user  = self.env.user
        
        if len(fotocasa_tops) >= user.company_id.fotocasa:
            raise except_orm(_('Limit excedido!'),
                _('Ha superado el limite de Fotocasa'))
        
        return True
    
    
    fotocasa = fields.Boolean('Publicado en fotocasa.com')
    
    
    
    