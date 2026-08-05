# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    current_cash_balance = fields.Monetary(
        string='Current Balance',
        compute='_compute_current_cash_balance',
        currency_field='currency_id',
    )
    cash_transfer_count = fields.Integer(
        string='Transfers Count',
        compute='_compute_cash_transfer_count',
    )

    def _compute_current_cash_balance(self):
        for journal in self:
            if journal.default_account_id:
                domain = [
                    ('account_id', '=', journal.default_account_id.id),
                    ('parent_state', '=', 'posted'),
                ]
                res = self.env['account.move.line']._read_group(
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
            }
        }
