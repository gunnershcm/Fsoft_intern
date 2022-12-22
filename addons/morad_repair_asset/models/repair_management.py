import string
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class RepairManagement(models.Model):
    _name = "repair.management"
    _description = "Asset Repair Management"
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'ref'

    def button_confirm(self):      
        self.state = 'confirm'
    def button_quote(self):      
        self.state = 'quote'
    def button_approve(self):      
        self.state = 'approved'
    def button_execute(self):      
        self.state = 'execute'
    def button_validate(self):      
        self.state = 'validate'
    def button_close(self):      
        self.state = 'close'
    def button_draft(self):      
        self.state = 'draft'
    def button_cancel(self):      
        self.state = 'cancel'

    #reference id
    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('repair.management')
        return super(RepairManagement, self).create(vals)

    @api.depends('service_ids')
    def _compute_service_price(self):
        for rec in self:
            rec.service_untaxed = sum(rec.service_ids.mapped('service_unit_price'))
            rec.service_tax = sum(rec.service_ids.mapped('tax_amount'))
            rec.service_total = sum(rec.service_ids.mapped('total'))

    @api.depends('sparepart_line_ids')
    def _compute_sparepart_price(self):
        for rec in self:
            rec.sparepart_untaxed = sum(rec.sparepart_line_ids.mapped('sparepart_untaxed'))
            rec.sparepart_tax = sum(rec.sparepart_line_ids.mapped('tax_amount'))
            rec.sparepart_total = sum(rec.sparepart_line_ids.mapped('total'))

    @api.onchange('service_total', 'sparepart_total')
    def _compute_total(self):
        for record in self:
            record.total = record.service_total + record.sparepart_total

    id = fields.Char(string='Request ID')
    partner_id = fields.Many2one('res.partner', string='Vendor', tracking=True, readonly=True, states={'draft': [('readonly', False)]}, required=True)
    request_date = fields.Datetime(string='Request Date', tracking=True, default=fields.Datetime.now, readonly=True, states={'draft': [('readonly', False)]})
    finish_date = fields.Datetime(string='Finish Date', readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text()
    active = fields.Boolean(default=True)
    ref = fields.Char(string='Reference', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('quote', 'Quotation'),
                              ('approving', 'Approving'),
                              ('approved', 'Approved'),
                              ('execute', 'Executing'),
                              ('validate', 'Validating'),
                              ('close', 'Closed'),
                              ('cancel', 'Cancelled')],
                              default='draft', string="Status", required=True)
    asset_detail_id = fields.Many2one('account.asset.asset', string='Asset Detail', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    asset_detail_residual = fields.Monetary(related='asset_detail_id.value_residual', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')]).id)
    service_ids = fields.Many2many('repair.service', string='Services', readonly=True, states={'quote': [('readonly', False)]})
    
    service_untaxed = fields.Monetary(compute='_compute_service_price', string='Orginal Service Price')
    service_tax = fields.Monetary(compute='_compute_service_price', string='Service Tax')
    service_total = fields.Monetary(compute='_compute_service_price', string='Service Price')
    
    sparepart_untaxed = fields.Monetary(compute='_compute_sparepart_price', string='Orginal Spare Part Price')
    sparepart_tax = fields.Monetary(compute='_compute_sparepart_price', string='Spare Part Tax')
    sparepart_total = fields.Monetary(compute='_compute_sparepart_price', string='Spare Part Price')

    sparepart_line_ids = fields.One2many('repair.management.part.selection', 'ticket_id', string='Spare Parts', readonly=True, states={'quote': [('readonly', False)]})
    total = fields.Monetary(compute='_compute_total', string='Total')
