from email.policy import default
from operator import index
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class AccountAssetDetailDeprecicationLine(models.Model):
    _name = 'account.asset.detail.depreciation.line'
    _description = 'Asset/Asset Detail/Depreciation Line'

    asset_detail_id = fields.Many2one('account.asset.detail', string='Depreciation Lines')
    amount = fields.Float(string='Current Depreciation')
    remaining_value = fields.Float(string='Next Period Depreciation')
    depreciated_value = fields.Float(string='Cumulative Depreciation')
    depreciation_date = fields.Date('Depreciation Date')
    

class AccountAssetDetail(models.Model):
    _name = 'account.asset.detail'
    _description = 'Asset/Asset Detail'
    _rec_name = 'asset_detail_id'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    asset_detail_id = fields.Char(string='Asset Detail Code', required=True, index=True)
    detail_quantity = fields.Integer(string='Quantity', required=True, default=1)
    name = fields.Char(string='Asset Detail Name', readonly=True, related='asset_id.name')

    asset_id = fields.Many2one('account.asset.asset', string='Asset', required=True, ondelete='cascade')
    asset_type_ext = fields.Selection(string='Asset Type', related='product_id.asset_type_ext')
    cur_asset_detail_qty = fields.Integer(string='Current Detail Quantity', related='asset_id.asset_detail_quantity')
    avail_asset_detail_qty = fields.Integer(string='Available Asset Detail Quantity', compute='_compute_avail_detail_qty')
    max_asset_detail_qty = fields.Integer(string='Max Detail Quantity', related='asset_id.max_asset_detail_qty')
    depreciation_line_ids = fields.One2many('account.asset.detail.depreciation.line', 'asset_detail_id', 
                                            # related='asset_id.depreciation_line_ids',
                                            string='Depreciation Lines', readonly=True)

    product_id = fields.Many2one(string='Product', required=True, ondelete='cascade', related='asset_id.product_id')
    product_qty = fields.Float(string='Product Quantity', related='asset_id.product_qty', readonly=True, digits=(9, 0))
    product_type = fields.Selection(string='Product Type', related='asset_id.product_type', readonly=True)
    total_asset_detail_quantity = fields.Integer(string='Asset Detail Quantity', readonly=True, related='asset_id.asset_detail_quantity')
    avail_product_qty = fields.Float(string='Available Quantity', digits=(9, 0),
                                        compute='_compute_avail_prod_qty', readonly=True)

    state = fields.Selection([('draft', 'Draft'), ('avail', 'Available'), ('cancel', 'Canceled')], 
                             string='Status', required=True, copy=False, default='draft')

    def set_draft(self):
        self.state = "draft"

    def confirm_action(self):
        self.state = "avail"

    def cancel_action(self):
        self.state = "cancel"

    @api.depends("product_id")
    def _compute_avail_detail_qty(self):
        for item in self:
            item.avail_asset_detail_qty = min(item.max_asset_detail_qty - item.cur_asset_detail_qty, item.avail_product_qty)

    @api.depends("product_id")
    def _compute_avail_prod_qty(self):
        for item in self:
            # item.avail_product_qty = item.product_qty - item.total_asset_detail_quantity
            # item.avail_product_qty = item.product_qty - item.asset_id.available_quantity
            item.avail_product_qty = item.asset_id.available_quantity

    @api.model
    @api.onchange("detail_quantity")
    def _check_values(self):
        error = False
        if self.detail_quantity <= 0:
            error = True
        if error == True:
            raise ValidationError(
                _("Quantity must be a greater than 0!")
            )
   
    @api.onchange('asset_detail_id')
    def _check_duplicate_id(self):
        if not self.asset_detail_id: return

        domain = [('asset_detail_id', '=', self.asset_detail_id)]

        if self.env['account.asset.detail'].search(domain, limit=1):
            raise ValidationError(
                _("The asset detail code '%s' already exists.", self.asset_detail_id)
            )

    @api.model
    def create(self, vals):
        res = super(AccountAssetDetail, self).create(vals)
        # count_product = 0
        # for item in self.env["product.template"].search([]):
        #     if item.id == res.product_id.id:
        #         if item.detailed_type == 'product':
        #             count_product = count_product + item.qty_available
        #         if item.detailed_type == 'consu':
        #             count_product = count_product + item.purchased_product_qty
        # print("product qty: ", count_product)

        # asset_detail_qty = 0
        # for item in self.env["account.asset.detail"].search([]):
        #     if item.product_id.id == res.product_id.id:
        #         asset_detail_qty = asset_detail_qty + item.detail_quantity
        # print("asset detail qty: ", asset_detail_qty)

        # if asset_detail_qty > count_product:
        print(res.avail_asset_detail_qty)
        if res.asset_type_ext == 'identical' and res.avail_asset_detail_qty <= 0:
            msg = "Not enough product to create asset detail!\n"
            p_msg = f"Product quantity: {res.max_asset_detail_qty}\n"
            a_msg = f"Asset detail quantity: {res.cur_asset_detail_qty - 1}"
            raise ValidationError(
                _(msg + p_msg + a_msg)
            )

        lines_dict = {
            'asset_id': res.asset_id.id,
            'product_id': res.product_id.default_code,
            'asset_detail_id': res.asset_detail_id,
            'quantity': res.detail_quantity
        }
        self.env['account.asset.detail.log'].create(lines_dict)
        return res

    def display_depreciation(self):
        # domain = [('asset_id', '=', self.asset_id)]    
        domain = [('asset_detail_id', '=', self.asset_detail_id)]
        depreciation_line_ids = self.env['account.asset.detail.depreciation.line'].search(domain)
        commands = [(2, line_id.id, False) for line_id in depreciation_line_ids]

        if self.asset_id.value_residual != 0.0:
            for depreciation_line in self.env['account.asset.depreciation.line'].search([]):
                if depreciation_line.asset_id != self.asset_id: continue
                qty = self.max_asset_detail_qty
                vals = {
                    'asset_detail_id': self.asset_detail_id,
                    'amount': depreciation_line.amount / qty,
                    'remaining_value': depreciation_line.remaining_value / qty,
                    'depreciated_value': depreciation_line.depreciated_value / qty,
                    'depreciation_date': depreciation_line.depreciation_date,
                }
                commands.append((0, False, vals))

        self.write({'depreciation_line_ids': commands})

        return True

    def name_get(self):
        self.browse(self.ids).read(['name', 'asset_detail_id'])
        return [(template.id, '%s%s' % (template.asset_detail_id and '[%s] ' % template.asset_detail_id or '', template.name))
                for template in self]