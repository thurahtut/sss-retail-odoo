from odoo import api, models, fields, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        self._onchange_mobile_validation()
        self._onchange_phone_validation()
        return res
