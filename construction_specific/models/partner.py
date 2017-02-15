from openerp import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['country_id'] = None
        return models.Model.create(self, vals)
