# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ignacio Ibeas Izquierdo <ignacio@acysos.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.depends('config_id', 'statement_ids')
    def _compute_cash_all(self):
        super(PosSession, self)._compute_cash_all()
        for session in self:
            if session.config_id.cashdro_payment_terminal:
                for statement in session.statement_ids:
                    if statement.journal_id.type == 'cash':
                        session.cash_control = True
                        session.cash_journal_id = statement.journal_id.id
                        session.cash_register_id = statement.id
                if not session.cash_control and session.state != 'closed':
                    raise UserError(_("Cash control can only be applied to cash journals."))
