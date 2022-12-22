from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class RepairSparePart(models.Model):
    _name = 'repair.sparepart'
    _description = 'Repair Spare Parts'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'sparepart_name'

    ref = fields.Char(string='Reference')
    sparepart_name = fields.Char(string='Name')
    sparepart_category = fields.Char(string='Category')
    sparepart_quantity = fields.Integer(string='Quantity', default=1)
    sparepart_unit_price = fields.Monetary(string = 'Unit Price')
    tax = fields.Many2one('account.tax', string='Tax')

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')]).id)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    active = fields.Boolean(default=True)

class TicketSparePartSelection(models.Model):
    _name="repair.management.part.selection"
    _description="Repair Management Spare Parts Selection"

    @api.onchange('sparepart_unit_price', 'sparepart_quantity')
    def _compute_tax(self):
        for rec in self:
            rec.sparepart_untaxed = rec.sparepart_unit_price * rec.sparepart_quantity
            if rec.tax:
                rec.tax_amount = rec.tax.amount/100 * rec.sparepart_untaxed                
            else:
                rec.tax_amount = 0
            rec.total = rec.tax_amount + rec.sparepart_untaxed 

    sparepart_id = fields.Many2one('repair.sparepart', string="Spare Parts")
    sparepart_name = fields.Char(related="sparepart_id.sparepart_name", string='Name')
    sparepart_unit_price = fields.Monetary(related="sparepart_id.sparepart_unit_price", string='Unit Price')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')]).id)
    sparepart_quantity = fields.Integer(string='Quantity', default=1)
    #Tax
    tax = fields.Many2one('account.tax', string='Tax')
    sparepart_untaxed = fields.Monetary(compute='_compute_tax', string='Untax Price', readonly=True)
    tax_amount=fields.Monetary(compute='_compute_tax', string="Tax Amount")
    total = fields.Monetary(compute='_compute_tax', string='Spare Part Total', readonly=True)

    note = fields.Text(string='Note')
    ticket_id= fields.Many2one('repair.management', string='Repairment Ticket')
