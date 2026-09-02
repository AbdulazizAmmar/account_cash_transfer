# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_journal_ids = fields.Many2many(
        'account.journal',
        'account_journal_res_users_rel',
        'user_id',
        'journal_id',
        string='Allowed Cash Journals',
        domain="[('type', 'in', ['cash', 'bank'])]",
        help='Cash and Bank journals this user is authorized to access and transfer between.'
    )
    pinned_journal_id = fields.Many2one(
        'account.journal',
        string='Pinned Journal',
        domain="[('type', 'in', ['cash', 'bank'])]",
        help='The primary/pinned journal for this user shown at the top of the kanban dashboard.',
        ondelete='set null',
    )

    def action_pin_journal(self, journal_id):
        """Pin a journal as the primary journal for the current user."""
        self.ensure_one()
        if self.pinned_journal_id and self.pinned_journal_id.id == journal_id:
            # Unpin if clicking the same journal again
            self.sudo().write({'pinned_journal_id': False})
        else:
            self.sudo().write({'pinned_journal_id': journal_id})
        return True
