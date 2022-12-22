from datetime import datetime

from requests import options
from odoo import api, fields, models

class AccountAssetDetailLog(models.Model):
    _name = 'account.asset.detail.log'
    _description = 'Asset/Asset Detail Log'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'asset_detail_id'

    log_time = fields.Datetime(string='Logging Time', default=lambda self: fields.Datetime.now())
    asset_id = fields.Many2one('account.asset.asset', string='Asset Code')   
    product_id = fields.Char(string='Product Code')
    asset_detail_id = fields.Char(string='Asset Detail Code')
    quantity = fields.Integer(string='Asset Quantity')
    