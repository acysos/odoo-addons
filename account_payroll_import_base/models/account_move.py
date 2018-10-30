from odoo import fields, models, api, _

class AccountMove(models.Model):
    _inherit = "account.move"
    
    import_file_id = fields.Many2one(
        comodel_name='import.file', string='Import')
    