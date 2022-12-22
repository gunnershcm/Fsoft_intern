# -*- coding: utf-8 -*-
from email.policy import default
from importlib.metadata import requires
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class Deploy(models.Model):
    _name = "deploy"
    _description = "deploy model"
    _rec_name = "deploy_id"
    _inherit = ['mail.thread','mail.activity.mixin']

    deploy_id = fields.Char(string="Deploy ID", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    warehouse_id = fields.Many2one('stock.warehouse', string='From')    #model: stock
    partner_id = fields.Many2one('res.partner',string='To')             #model: product
    note = fields.Text('Note')

    ticket_created_time = fields.Datetime('Ticket created time', required=False)
    requested_time = fields.Datetime('Requested time', required=False)
    plan_deploy_time  = fields.Datetime('Plan deploy time ', required=False)
    actual_deploy_time = fields.Datetime('Actual deploy time', required=False)
    stock_in_time = fields.Datetime('Stock in time', required = False)

    total = fields.Integer(string="Total",compute="_count_total", store=True )
    total_residual = fields.Integer(string="Total Residual",compute="_count_total_residual", store=True )

    asset_demand_line_ids = fields.One2many("deploy.demand", "deploy_id", string="Demand Lines")
    asset_asset_line_ids = fields.One2many("deploy.asset", "deploy_id", string="Asset Lines")

    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approving', 'Approving '),
                              ('approved', 'Approved '),
                              ('delivered', 'Delivered'),
                              ('deployed', 'Deployed'),
                              ('validated', 'Validated'),
                              ('closed', 'Closed'),
                              ('cancelled', 'Cancelled')],
                               default='draft' ,string="Status")
    

    def action_confirmed(self):
        self.write({'state': 'confirmed'})
        for line in self.asset_asset_line_ids:
            line.status = 'available'
        return

    def action_approving(self):
        self.write({'state': 'approving'})
        return   

    def action_approved(self):
        self.write({'state': 'approved'})
        return

    def action_delivered(self):
        self.write({'state': 'delivered'})
        return

    def action_deployed(self):
        self.write({'state': 'deployed'})
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

    @api.depends('total', 'asset_demand_line_ids', 'asset_demand_line_ids.quantity')
    def _count_total(self):
        for rec in self:
            total_amount = 0.0
            for line in rec.asset_demand_line_ids:
                total_amount = total_amount + line.quantity
                rec.total = total_amount
    
    @api.depends('total_residual', 'asset_asset_line_ids', 'asset_asset_line_ids.value_residual')
    def _count_total_residual(self):
        for rec in self:
            total_amount = 0.0
            for line in rec.asset_asset_line_ids:
                total_amount = total_amount + line.value_residual
                rec.total_residual = total_amount 
    

    @api.model
    def create(self, vals):
        if vals.get('deploy_id', _('New')) ==  _('New'):
            vals['deploy_id'] = self.env['ir.sequence'].next_by_code('deploy') or _('New')
        res = super(Deploy, self).create(vals)
        if res.asset_demand_line_ids:
            for line in res.asset_demand_line_ids:
                newLine = []
                for record in range(line.quantity):
                    values = {
                        'asset_detail_id' : line.asset_detail_id.id,
                        'quantity' : 1,
                        'status'   : 'process'
                    }
                    newLine.append((0,0,values))
                res.asset_asset_line_ids = newLine      
        return res

    def write(self, vals):     
        # print("________________")
        # domain = [('deploy_id', '=', self.deploy_id)]
        # demand_lines = self.env['deploy.demand'].search(domain)
        # for line in demand_lines:
        #     print("Demand: ", line.id, line.asset_detail_id.asset_id, line.quantity)
        # commands = [(2, line_id.id, False) for line_id in demand_lines]

        # if vals.get('asset_demand_line_ids'):
        #     # print("Lines: ", vals.get('asset_demand_line_ids'))
        #     for line in vals.get('asset_demand_line_ids'):
        #         print("Lines: ", line)
        #         for rec in line:
        #             if type(rec) is dict:
        #                 print("Rec: ", rec)
        #                 qty = 1 if rec.get('quantity') == None else rec.get('quantity')
        #                 for record in range(qty):
        #                     values = {
        #                         'asset_detail_id' : rec.get('asset_detail_id'),
        #                         'quantity' : 1
        #                     }
        #                     commands.append((0, 0, values))  
        # res = super(Deploy, self).write({"asset_asset_line_ids": commands})        
        # return res
        if vals.get('asset_demand_line_ids'):
            for line in vals.get('asset_demand_line_ids'):
                for rec in line:
                    newLine = []
                    if type(rec) is dict:
                        for record in range(rec.get('quantity')):
                            values = {
                                'asset_detail_id' : rec.get('asset_detail_id'),
                                'quantity' : 1
                            }
                            newLine.append((0,0,values))  
                        vals['asset_asset_line_ids'] = newLine   
        res = super(Deploy, self).write(vals)        
        return res
    
class DeployDemand(models.Model):
    _name = "deploy.demand"
    _description = "Deploy Demand"

    asset_detail_id = fields.Many2one("account.asset.detail", string='Asset Detail')
    category_id = fields.Many2one('account.asset.category', string='Category', related="asset_detail_id.asset_id.category_id")
    quantity = fields.Integer(string="Quantity")

    name = fields.Char(string='Asset Name', related="asset_detail_id.asset_id.name")
    deploy_id = fields.Many2one('deploy', string='Deploy Code')
    
    warehouse_id = fields.Many2one(string='Warehouse',related='deploy_id.warehouse_id')

class DeployAsset(models.Model):
    _name = "deploy.asset"
    _description = "Deploy Asset"

    asset_detail_id = fields.Many2one("account.asset.detail",string='Asset Detail')
    category_id = fields.Many2one('account.asset.category', string='Category',
                                  related="asset_detail_id.asset_id.category_id")
    quantity = fields.Integer(string="Quantity")

    name = fields.Char(string='Asset Name',related="asset_detail_id.asset_id.name")
    value = fields.Monetary(string='Gross Value', related="asset_detail_id.asset_id.value")
    value_residual = fields.Monetary(string='Residual Value', related="asset_detail_id.asset_id.value_residual")

    currency_id = fields.Many2one('res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    deploy_id = fields.Many2one('deploy', string='deploy_id')
    warehouse_id = fields.Many2one(string='Warehouse',related='deploy_id.warehouse_id')
    partner_id = fields.Many2one(string='Partner',related='deploy_id.partner_id')
    status = fields.Char('Status')



   

