# -*- coding: utf-8 -*-
{
    'name': 'Account Cash Transfer',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Internal cash/bank journal transfers with automatic journal entries',
    'description': """
        Handle bank reconciliation and internal transfers from one cash/bank
        journal to another. Automatically generates paired journal entries
        using the company's internal transfer account.
    """,
    'author': 'Custom',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_cash_transfer_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
