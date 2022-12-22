# -*- coding: utf-8 -*-
from email.policy import default
from signal import valid_signals
from importlib.metadata import requires
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class Withdraw(models.Model):
    _name = "withdraw"
    _description = "withdraw model"
    _rec_name = "withdraw_id"
    _inherit = ['mail.thread','mail.activity.mixin']

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})
    withdraw_id = fields.Char('Ticket Code', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner',string='From') 
    warehouse_id = fields.Many2one('stock.warehouse', string='To')
    note = fields.Text('Note')

    ticket_created_time = fields.Datetime('Ticket created time', required=False)
    requested_time = fields.Datetime('Requested time', required=False)
    plan_withdraw_time  = fields.Datetime('Plan withdraw time ', required=False)
    actual_withdraw_time = fields.Datetime('Actual withdraw time', required=False)
    stock_in_time = fields.Datetime('Stock in time', required = False)


    deploy_id = fields.Many2one("deploy", string='Asset Datil')



    # total = fields.Integer(string="Total",compute="_count_total", store=True )
    # total_residual = fields.Integer(string="Total Residual",compute="_count_total_residual", store=True )

    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approving', 'Approving '),
                              ('approved', 'Approved '),
                              ('picked', 'Picked'),
                              ('stored', 'Stored'),
                              ('validated', 'Validated'),
                              ('closed', 'Closed'),
                              ('cancelled', 'Cancelled')],
                               default='draft' ,string="Status")
                               
    deploy_ids = fields.Many2many('deploy', string='Deploy IDs')
    asset_info_id = fields.Many2many('deploy.asset', string='Deploy asset ID')

    @api.onchange('deploy_ids')
    def onchange_deploy_ids(self):
        self.asset_info_id = self.deploy_ids.asset_asset_line_ids

    @api.onchange('state')
    def onchange_deploy_ids(self):
        for line in self.deploy_ids.asset_asset_line_ids:
            line.status = 'available'


    # @api.onchange('asset_info_id')
    def onchange_deploy_ids(self):
        for line in self.asset_info_id:
            line.status = 'process'

    
    
    # asset_id = fields.Many2one("account.asset.asset", string='Asset')
    # asset_category_id = fields.Many2one("account.asset.category",string='Asset_Category')

    # asset_demand_line_ids = fields.One2many("withdraw.demand","withdraw_id",string="Demand lines")
    # asset_asset_line_ids = fields.One2many("withdraw.asset","withdraw_id",string="Asset lines")

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        for line in self.asset_info_id:
            line.status = 'available'
        return

    def action_approving(self):
        self.write({'state': 'approving'})
        return   

    def action_approved(self):
        self.write({'state': 'approved'})
        return

    def action_picked(self):
        self.write({'state': 'picked'})
        return

    def action_stored(self):
        self.write({'state': 'stored'})
        return

    def action_validated(self):
        self.write({'state': 'validated'})
        return

    def action_closed(self):
        self.write({'state': 'closed'})
        return

    def action_cancelled(self):
        self.write({'state': 'cancelled'})
        return

    def action_draft(self):
        self.write({'state': 'draft'})
        return 

    # @api.depends('total', 'asset_demand_line_ids', 'asset_demand_line_ids.quantity')
    # def _count_total(self):
    #     for rec in self:
    #         total_amount = 0.0
    #         for line in rec.asset_demand_line_ids:
    #             total_amount = total_amount + line.quantity
    
    #             rec.total = total_amount 
    
    @api.depends('total_residual', 'asset_asset_line_ids', 'asset_asset_line_ids.value_residual')
    def _count_total_residual(self):
        for rec in self:
            total_amount = 0.0
            for line in rec.asset_asset_line_ids:
                total_amount = total_amount + line.value_residual
                rec.total_residual = total_amount 
    

    @api.model
    def create(self, vals):
        if vals.get('withdraw_id', _('New')) ==  _('New'):
            vals['withdraw_id'] = self.env['ir.sequence'].next_by_code('withdraw') or _('New')
        
        
        res = super(Withdraw, self).create(vals)
        res.onchange_deploy_ids()
        return res

    def write(self, vals):
        # if vals.get('asset_demand_line_ids'):
        #     for line in vals.get('asset_demand_line_ids'):
        #             for rec in line:
        #                 newLine = []
        #                 if type(rec) is dict:
        #                     for record in range(rec.get('quantity')):
        #                         values = {
        #                             'asset_id' : rec.get('asset_id'),
        #                             'quantity' : 1
        #                         }
        #                         newLine.append((0,0,values))  
        #                     vals['asset_asset_line_ids'] = newLine   
        
        res = super(Withdraw, self).write(vals)
        self.onchange_deploy_ids()
        return res
      

   
# class WithdrawDemand(models.Model):
#     _name = "withdraw.demand"
#     _description = "Withdraw Demand"
#     _inherit = "withdraw"


#     asset_id = fields.Many2one("account.asset.asset",string='Asset')
#     category_id = fields.Many2one('account.asset.category', string='Category',
#                                   related="asset_id.category_id")
#     quantity = fields.Integer(string="Quantity")

#     name = fields.Char(string='Asset Name',related="asset_id.name")
#     # withdraw_id = fields.Many2one('withdraw', string='withdraw_id')


# class WithdrawAsset(models.Model):
#     _name = "withdraw.asset"
#     _description = "Withdraw Asset"

    # currency_id = fields.Many2one('res.currency', string='Currency', required=True,
    #                               readonly=True, states={'draft': [('readonly', False)]},gory', string='Category',
    #                               related="asset_id.category_id")
    # quantity = fields.Integer(string="Quantity")

    # value = fields.Monetary(string='Gross Value', related="asset_id.value")
    # value_residual = fields.Monetary(string='Residual Value', related="asset_id.value_residual")

    # currency_id = fields.Many2one('res.currency', string='Currency', required=True,
    #                               readonly=True, states={'draft': [('readonly', False)]},
    #     default=lambda self: self.env.user.company_id.currency_id.id)
    # company_id = fields.Many2one('res.company', string='Company', required=True,
    #                              readonly=True, states={'draft': [('readonly', False)]},
    #                              default=lambda self: self.env.company)
    # withdraw_id = fields.Many2one('withdraw', string='withdraw_id')



   

