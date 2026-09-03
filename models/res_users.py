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
    pinned_journal_ids = fields.Many2many(
        'account.journal',
        'account_journal_pinned_users_rel',
        'user_id',
        'journal_id',
        string='Pinned Journals',
        domain="[('type', 'in', ['cash', 'bank'])]",
        help='Journals pinned to the top of the kanban dashboard for this user.',
    )

    def action_pin_journal(self, journal_id):
        """Toggle pin for a journal. Adds if not pinned, removes if already pinned."""
        self.ensure_one()
        journal = self.env['account.journal'].browse(journal_id)
        if journal in self.sudo().pinned_journal_ids:
            self.sudo().write({'pinned_journal_ids': [(3, journal_id)]})
        else:
            self.sudo().write({'pinned_journal_ids': [(4, journal_id)]})
        return True
