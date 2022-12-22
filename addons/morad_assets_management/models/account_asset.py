from email.policy import default
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class AccountAsset(models.Model):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'
    _description = 'Asset'
    # _inherit = ['mail.thread','mail.activity.mixin']

    product_id = fields.Many2one('product.template', string='Product', ondelete='cascade')
    asset_type_ext = fields.Selection(string='Asset Type', related='product_id.asset_type_ext')
    asset_detail_ids = fields.One2many('account.asset.detail', 'asset_id', string='Asset Detail', ondelete='cascade')
    asset_detail_log_ids = fields.One2many('account.asset.detail.log', 'asset_id', string='Asset detail log')
    editable_detail = fields.Boolean(compute='compute_edtiable_detail', default=False)

    category_id = fields.Many2one('account.asset.category', string='Category', related='product_id.asset_category_id')
    # partner_id = fields.Many2one('res.partner', string='Partner', related='product_id.seller_ids')
    product_qty = fields.Float(string='Product Quantity', compute='_compute_product_quantity', readonly=True, digits=(9, 0))
    product_type = fields.Selection(string='Product Type', related='product_id.detailed_type', readonly=True)
    asset_detail_quantity = fields.Integer(string='Asset Detail Quantity', readonly=True, compute='_compute_asset_detail_quantity')
    available_quantity = fields.Integer(string='Available Quantity', readonly=True, compute='_compute_avail_qty')

    max_asset_detail_qty = fields.Integer(string='Max Detail Quantity', required=True, default=1)

    @api.model
    @api.constrains('max_asset_detail_qty')
    def _check_value(self):
        max_qty = 1 if self.product_qty == 0 else self.product_qty
        if self.max_asset_detail_qty > max_qty or self.max_asset_detail_qty < 1:
            raise ValidationError(_('Maximum asset detail quantity must be between 1 and %d (product quantity).', max_qty))

    @api.depends("product_id", "invoice_id")
    def _compute_max_qty(self):
        for asset in self:
            max_qty = 0
            for invoice in self.env["account.move"].search([]):
                if invoice.id == asset.invoice_id.id:
                    for line in self.env["account.move.line"].search([('move_id', '=', invoice.id)]):
                        # print("_________________")
                        # print(asset.product_id.id, line.product_id.product_tmpl_id)
                        if line.product_id.product_tmpl_id.id == asset.product_id.id and line.product_id != False:
                            # print("Qty: ", line.quantity)
                            max_qty = max_qty + line.quantity
            asset.max_asset_detail_qty = max_qty

    @api.depends("product_id", "invoice_id")
    def _compute_product_quantity(self):
        for asset in self:
            max_qty = 0
            # print(asset.invoice_id.id)
            if asset.invoice_id.id > 0:
                for invoice in self.env["account.move"].search([]):
                    if invoice.id == asset.invoice_id.id:
                        for line in self.env["account.move.line"].search([('move_id', '=', invoice.id)]):
                            if line.product_id.product_tmpl_id.id == asset.product_id.id and line.product_id != False:
                                max_qty = max_qty + line.quantity
            else: 
                for product in self.env["product.template"].search([]):
                    if product.id == asset.product_id.id:
                        if product.detailed_type == 'product':
                            max_qty = max_qty + product.qty_available
                        if product.detailed_type == 'consu':
                            max_qty = max_qty + product.purchased_product_qty - product.sales_count
            asset.product_qty = max_qty
    
    @api.depends("product_id")
    def _compute_asset_detail_quantity(self):
        for asset in self:
            asset_detail_qty = 0
            for item in self.env["account.asset.detail"].search([]):
                if item.asset_id.id == asset.id:
                    asset_detail_qty = asset_detail_qty + item.detail_quantity
            asset.asset_detail_quantity = asset_detail_qty

    @api.depends("product_id", "invoice_id")
    def _compute_avail_qty(self):
        for asset in self:
            count_avail_qty = 0
            for item in self.env["account.asset.detail"].search([]):
                if asset.invoice_id.id == item.asset_id.invoice_id.id and asset.product_id.id == item.asset_id.product_id.id:
                    count_avail_qty = count_avail_qty + item.detail_quantity
            asset.available_quantity = asset.product_qty - count_avail_qty
    
    @api.model
    @api.onchange("product_id")
    def _copy_asset_name(self):
        self.name = self.product_id.name

    @api.onchange("product_id")
    def compute_edtiable_detail(self):
        if len(self.asset_detail_ids) > 0:
            self.editable_detail = True
            return
        self.editable_detail = False

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'code'])
        return [(template.id, '%s%s' % (template.code and '[%s] ' % template.code or '', template.name))
                for template in self]

    @api.constrains('asset_detail_ids')
    def _check_detail_lines(self):
        for record in self:
            if record.asset_type_ext == 'identical':
                if len(record.asset_detail_ids) > 1:
                    raise ValidationError(
                    _("Identical assets can only have 1 detail code!")
                )