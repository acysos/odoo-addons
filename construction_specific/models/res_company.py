from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    human_cost = fields.Float(string='Coste mano de obra')
    sign1 = fields.Binary(string="Firma 1")
    sign2 = fields.Binary(string="Firma 2")
