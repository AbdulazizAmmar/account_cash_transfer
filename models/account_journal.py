# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.fields import Domain


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    allowed_user_ids = fields.Many2many(
        'res.users',
        'account_journal_res_users_rel',
        'journal_id',
        'user_id',
        string='Allowed Transfer Users',
        help='Users allowed to view and perform cash transfers with this journal. If empty, all authorized users can access it.'
    )
    current_cash_balance = fields.Monetary(
        string='Current Balance',
        compute='_compute_current_cash_balance',
        currency_field='currency_id',
    )
    cash_transfer_count = fields.Integer(
        string='Transfers Count',
        compute='_compute_cash_transfer_count',
    )
    is_pinned_for_user = fields.Boolean(
        string='Pinned',
        compute='_compute_is_pinned_for_user',
        help='Whether this journal is pinned as primary for the current user.',
    )

    def _compute_is_pinned_for_user(self):
        pinned_id = self.env.user.pinned_journal_id.id
        for journal in self:
            journal.is_pinned_for_user = (journal.id == pinned_id)

    def action_toggle_pin(self):
        """Toggle pin state of this journal for the current user."""
        self.ensure_one()
        self.env.user.action_pin_journal(self.id)
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        if self.env.context.get('restrict_journal_access'):
            user = self.env.user
            is_full_access = (
                user.has_group('account_cash_transfer.group_cash_transfer_manager') or
                user.has_group('account.group_account_manager') or
                user.has_group('account.group_account_user') or
                self.env.is_admin()
            )
            if not is_full_access:
                if user.allowed_journal_ids:
                    # User has specific assigned journals: ONLY show assigned journals
                    journal_domain = [('id', 'in', user.allowed_journal_ids.ids)]
                else:
                    # User has no specific assigned journals: show open journals or journals assigned to user
                    journal_domain = ['|', ('allowed_user_ids', '=', False), ('allowed_user_ids', 'in', [user.id])]
                domain = Domain.AND([domain, journal_domain])
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)

    def _compute_current_cash_balance(self):
        for journal in self:
            if journal.default_account_id:
                domain = [
                    ('account_id', '=', journal.default_account_id.id),
                    ('parent_state', '=', 'posted'),
                ]
                res = self.env['account.move.line'].sudo()._read_group(
                    domain, aggregates=['balance:sum']
                )
                journal.current_cash_balance = res[0][0] if res and res[0][0] else 0.0
            else:
                journal.current_cash_balance = 0.0

    def _compute_cash_transfer_count(self):
        for journal in self:
            count = self.env['account.cash.transfer'].search_count([
                '|',
                ('from_journal_id', '=', journal.id),
                ('to_journal_id', '=', journal.id)
            ])
            journal.cash_transfer_count = count

    def action_view_transfers(self):
        self.ensure_one()
        return {
            'name': _('Transfers - %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'account.cash.transfer',
            'view_mode': 'list,form',
            'domain': [
                '|',
                ('from_journal_id', '=', self.id),
                ('to_journal_id', '=', self.id)
            ],
            'context': {
                'default_from_journal_id': self.id,
                'restrict_journal_access': True,
            }
        }

    def action_create_transfer(self):
        self.ensure_one()
        return {
            'name': _('New Cash Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.cash.transfer',
            'view_mode': 'form',
            'context': {
                'default_from_journal_id': self.id,
                'restrict_journal_access': True,
            }
        }
