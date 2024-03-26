# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    """Extend to add cost field."""

    _inherit = 'stock.quant'

    unit_cost = fields.Monetary("Unit Cost")
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.company_id.currency_id
    )

    @api.model
    def _get_inventory_fields_write(self):
        res = super()._get_inventory_fields_write()
        res += ['unit_cost', 'currency_id']
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        self.ensure_one()
        res = super()._get_inventory_move_values(qty, location_id, location_dest_id, out)
        if self.unit_cost:
            res['price_unit'] = self.unit_cost
        return res

