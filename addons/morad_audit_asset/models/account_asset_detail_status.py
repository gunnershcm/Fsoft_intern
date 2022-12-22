from email.policy import default
from odoo import fields, models, api, _

class AccountAssetDetailSatus(models.Model):
    _name = "account.asset.detail.status"
    _description = "Asset/Asset detail status"
    _rec_name = "status"

    # asset_detail_id = fields.One2many('account.asset.audit.detail', 'status', string="Asset detail code")
    status = fields.Char(string='Status')

    # @api.model    
    # def default_get(self, fields_list):        
    #     defaults = super(AccountAssetDetailSatus, self).default_get(fields_list)        
    #     defaults['status'] = 'Good'
    #     defaults['status'] = 'Well'
    #     print(defaults)
    #     return defaults