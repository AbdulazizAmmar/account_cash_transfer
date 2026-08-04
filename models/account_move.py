# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    cash_transfer_id = fields.Many2one(
        'account.cash.transfer',
        string='Cash Transfer',
        readonly=True,
        ondelete='set null',
        index=True,
    )
