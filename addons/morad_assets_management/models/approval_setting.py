from email.policy import default
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class ApprovalSetting(models.Model):
    _name = 'approval.setting'
    _description = 'Approval setting'
    _rec_name = 'request_type'

    request_type = fields.Selection([('AD', 'Asset Deployment'), 
                                    ('AW', 'Asset Withdrawal'), 
                                    ('AR', 'Asset Repair')], 
                                    string='Request Type', required=True)
    approval_level = fields.Integer(string='Approval level', compute='_compute_approval_level', store=True, inverse="_inverse_approval_level")
    user_group = fields.Many2many('res.groups', string='User group', required=True)

    @api.depends("request_type")
    def _compute_approval_level(self):
        for item in self:
            current_level = 0
            for it in self.env['approval.setting'].search([]):
                if item.request_type == it.request_type:
                    current_level = max(current_level, it.approval_level)
            item.approval_level = current_level + 1

    def _inverse_approval_level(self):
        pass

    @api.model
    def create(self, vals):
        res = super(ApprovalSetting, self).create(vals)
        # if not res.approval_level: return

        # domain = [('request_type', '=', res.request_type), ('approval_level', '=', res.approval_level)]
        # if self.env['approval.setting'].search(domain, limit=1):
        #     switcher = {
        #         'AD': "Asset Deployment",
        #         'AW': "Asset Withdrawal",
        #         'AR': "Asset Repair",
        #     }
        #     rtype = switcher.get(res.request_type)
        #     raise ValidationError(
        #          _("Approval level %s for %s had already existed!", 
        #             res.approval_level, rtype)
        #     )
        return res

    @api.onchange('approval_level')
    def _check_duplicate_id(self):
        if not self.approval_level: return

        domain = [('request_type', '=', self.request_type), ('approval_level', '=', self.approval_level)]
        if self.env['approval.setting'].search(domain, limit=1):
            switcher = {
                'AD': "Asset Deployment",
                'AW': "Asset Withdrawal",
                'AR': "Asset Repair",
            }
            rtype = switcher.get(self.request_type)
            raise ValidationError(
                 _("Approval level %s for %s had already existed!", 
                    self.approval_level, rtype)
            )