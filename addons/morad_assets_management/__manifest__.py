# -*- coding: utf-8 -*-
{
    'name': "MORAD ASM - Assets Management",
    'summary': """Assets management module""",
    'description': """Managing assets""",
    'author': "locnd15",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product', 'mail', 'web', 'account', 'om_account_asset'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset.xml',
        'views/account_asset_detail.xml',
        'views/account_asset_detail_log.xml',
        'views/approval_setting_views.xml',
    ],
    'installable': True,
    'application': True,
}
