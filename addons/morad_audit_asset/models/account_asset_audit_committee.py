from odoo import api, fields, models

class AccountAssetAuditCommittee(models.Model):
    _name = 'account.asset.audit.committee'
    _description = 'Asset/Asset audit committee'

    ticket_id = fields.Many2one('account.asset.audit.ticket', string='Ticket code')
    auditor_name = fields.Char(string='Name')
    is_lead = fields.Boolean(string='Is lead?', default=False)