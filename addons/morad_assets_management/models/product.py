from odoo import api, fields, models

class Product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    asset_type_ext = fields.Selection([('identical', 'Identical'), ('non-identical', 'Non-identical')],
                                   string='Asset Type', default='identical', required=True,
        help="Choose the type of the product to be stored as assets:\n"
           "  * Identical.\n"
           "  * Non-identical.")
        
    asset_category_id = fields.Many2one('account.asset.category', 
                                        string='Asset Category', company_dependent=True, ondelete="restrict")