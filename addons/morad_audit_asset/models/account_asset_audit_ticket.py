from datetime import datetime

from requests import options
from odoo import api, fields, models

class AccountAssetAuditTicket(models.Model):
    _name = 'account.asset.audit.ticket'
    _description = 'Asset/Asset audit ticket'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'ticket_id'

    ticket_id = fields.Char(string='Ticket code', required=True)
    ticket_created_time = fields.Datetime(string='Ticket created time', required=True, default=lambda self: fields.Datetime.now())
    auditor = fields.Char(string='Auditor', required=True)
    baseline_time = fields.Datetime(string='Baseline time')
    asset_quantity = fields.Integer(string='Asset quantity', compute='_compute_asset_quantity')
    ticket_description = fields.Text(string='Description')
    help_note = fields.Html(string="Help", required=True, compute="_get_default_note")

    def _get_default_note(self):
        result = """
            <div class="font-italic text-muted">
                (S) - System values<br/>(A) - Audit values
            </div>"""
        self.help_note = result    
        
    ticket_detail_ids = fields.One2many('account.asset.audit.detail', 'ticket_id', string='Audit detail', required=True)
    ticket_committee_ids = fields.One2many('account.asset.audit.committee', 'ticket_id', string='Audit committee', required=True)
    state = fields.Selection([('draft', 'Draft'), ('close', 'Closed'), ('cancel', 'Canceled')], 
                             string='Status', required=True, copy=False, default='draft')

    # @api.onchange('location')
    # def _onchange_location(self):
    #     fields = [
    #         'warehouse',
    #         'customer'
    #     ]
    #     ref_tracked_fields = self.env['account.asset.audit.ticket'].fields_get(fields)
    #     tracked_fields = ref_tracked_fields.copy()
    #     if self.location == 'warehouse':
    #         del(tracked_fields['customer'])
    #     if self.location == 'customer':
    #         del(tracked_fields['warehouse'])     
    # 

    # @api.multi
    def _compute_asset_quantity(self):     
        for asset_item in self:
            asset_item.asset_quantity = len(asset_item.ticket_detail_ids)                           

    def close_action(self):
        self.state = "close"

    def cancel_action(self):
        self.state = "cancel"