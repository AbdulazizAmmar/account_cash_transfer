# -*- coding: utf-8 -*-

from odoo import fields, models


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
