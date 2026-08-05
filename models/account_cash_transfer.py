# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCashTransfer(models.Model):
    _name = 'account.cash.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cash / Bank Internal Transfer'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        readonly=True,
        default='New',
        copy=False,
    )
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    from_journal_id = fields.Many2one(
        'account.journal',
        string='From Journal',
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]",
        tracking=True,
    )
    to_journal_id = fields.Many2one(
        'account.journal',
        string='To Journal',
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]",
        tracking=True,
    )
    note = fields.Text(
        string='Notes',
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    move_ids = fields.One2many(
        'account.move',
        'cash_transfer_id',
        string='Journal Entries',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'account.cash.transfer'
                ) or 'New'
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('from_journal_id', 'to_journal_id')
    def _check_journals_different(self):
        for rec in self:
            if rec.from_journal_id == rec.to_journal_id:
                raise UserError(_(
                    "The source and destination journals must be different."
                ))

    @api.constrains('amount')
    def _check_amount_positive(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_(
                    "The transfer amount must be greater than zero."
                ))

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    def action_confirm(self):
        """Confirm the transfer and create paired journal entries."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft transfers can be confirmed."))

            # Resolve the internal transfer account from the company
            transfer_account = rec.company_id.transfer_account_id
            if not transfer_account:
                raise UserError(_(
                    "Please configure an Internal Transfer Account on the "
                    "company '%s' before confirming.",
                    rec.company_id.name,
                ))

            # Resolve the default accounts of the journals
            from_account = rec.from_journal_id.default_account_id
            if not from_account:
                raise UserError(_(
                    "The journal '%s' does not have a default account set.",
                    rec.from_journal_id.name,
                ))

            to_account = rec.to_journal_id.default_account_id
            if not to_account:
                raise UserError(_(
                    "The journal '%s' does not have a default account set.",
                    rec.to_journal_id.name,
                ))

            # Build the dynamic label
            label = (
                "Cash transfer from %s to %s by %s at %s"
                % (
                    rec.from_journal_id.name,
                    rec.to_journal_id.name,
                    rec.user_id.name,
                    rec.date,
                )
            )

            # -----------------------------------------------------------------
            # Entry 1 – From Journal
            #   Credit  → from journal's default account
            #   Debit   → company internal transfer account
            # -----------------------------------------------------------------
            move_from_vals = {
                'journal_id': rec.from_journal_id.id,
                'date': rec.date,
                'ref': rec.name,
                'cash_transfer_id': rec.id,
                'line_ids': [
                    (0, 0, {
                        'name': label,
                        'account_id': from_account.id,
                        'credit': rec.amount,
                        'debit': 0.0,
                        'currency_id': rec.currency_id.id,
                    }),
                    (0, 0, {
                        'name': label,
                        'account_id': transfer_account.id,
                        'debit': rec.amount,
                        'credit': 0.0,
                        'currency_id': rec.currency_id.id,
                    }),
                ],
            }

            # -----------------------------------------------------------------
            # Entry 2 – To Journal
            #   Debit   → to journal's default account
            #   Credit  → company internal transfer account
            # -----------------------------------------------------------------
            move_to_vals = {
                'journal_id': rec.to_journal_id.id,
                'date': rec.date,
                'ref': rec.name,
                'cash_transfer_id': rec.id,
                'line_ids': [
                    (0, 0, {
                        'name': label,
                        'account_id': to_account.id,
                        'debit': rec.amount,
                        'credit': 0.0,
                        'currency_id': rec.currency_id.id,
                    }),
                    (0, 0, {
                        'name': label,
                        'account_id': transfer_account.id,
                        'credit': rec.amount,
                        'debit': 0.0,
                        'currency_id': rec.currency_id.id,
                    }),
                ],
            }

            # Create and post both journal entries
            moves = self.env['account.move'].create([move_from_vals, move_to_vals])
            moves.action_post()

            # Transition the state
            rec.state = 'confirmed'
