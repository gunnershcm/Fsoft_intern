{
    'name': "MORAD ASM - Repair Asset",
    'summary': """Repair asset module (MORAD - Asset Management)""",
    'description': """Managing Asset Repair""",
    'version': '1.0',
    'depends': [],
    'sequence':-100,
    'author': "ThanhLCH - HoangHDM",
    'category': 'Asset',
    'description': """
    A repair mangement module for tracking equipments being fixed and returned to company's asset.
    """,
    'license': 'LGPL-3',
    'depends':[
        'product', 'mail', 'web', 'account', 'om_account_asset'
    ],
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/repair_view.xml',
        'views/repair_service_view.xml',
        'views/repair_sparepart_view.xml',
        'data/sequence.xml',
        'views/partners.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
}