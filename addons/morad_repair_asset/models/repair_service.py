from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class RepairService(models.Model):
    _name = 'repair.service'
    _description = 'Repair Service'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name='service_name'

    @api.depends("service_unit_price")
    def _compute_tax(self):
        for rec in self:
            if rec.tax:
                rec.tax_amount = rec.tax.amount/100 * rec.service_unit_price                
            else:
                rec.tax_amount = 0
            rec.total = rec.tax_amount + rec.service_unit_price

    ref = fields.Char(string='Reference')
    service_name = fields.Char(string='Service Name')
    service_category = fields.Char(string='Category')
    service_unit_price = fields.Monetary(string='Unit Price')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')]).id)
    partner_id = fields.Many2one('res.partner', string='Vendor', tracking=True, store=True)
    active = fields.Boolean(default=True)

    #Calculate Taxed
    tax = fields.Many2one('account.tax', string='Tax')
    tax_amount=fields.Monetary(compute='_compute_tax', string="Tax Amount")
    total=fields.Monetary(compute='_compute_tax', string='Service Total')

