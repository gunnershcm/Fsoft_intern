# -*- coding: utf-8 -*-
{
    'name': "MORAD ASM - Withdraw Asset",
    'summary': """Withdraw asset module (MORAD - Asset Management)""",
    'description': """Managing Asset Withdrawal""",
    'author': "AnhDD18",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product',
        'mail',
        'account',
        'morad_deploy_asset',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/withdraw_views.xml',
        'views/data.xml',
    ],
    # 'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}