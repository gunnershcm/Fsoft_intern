# -*- coding: utf-8 -*-
{
    'name': "MORAD ASM - Deploy Asset",
    'summary': """Deploy asset module (MORAD - Asset Management)""",
    'description': """Managing Asset Deployment""",
    'author': "CuongHC6",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product',
        'mail',
        'account',
        'om_account_asset',
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/deploy_views.xml',
        'views/data.xml',
    ],
    # 'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}