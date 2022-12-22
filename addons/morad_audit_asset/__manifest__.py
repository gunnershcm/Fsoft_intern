# -*- coding: utf-8 -*-
{
    'name': "MORAD ASM - Audit Asset",
    'summary': """Audit asset module (MORAD - Asset Management)""",
    'description': """Managing Asset Audit""",
    'author': "locnd15",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product', 'mail', 'web', 'account', 'om_account_asset'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset_audit_ticket.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'morad_audit_asset/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
}
