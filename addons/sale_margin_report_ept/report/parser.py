import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportSaleMargin(models.AbstractModel):
    _name = 'report.sale_margin_report_ept.report_template'

    @api.model
    def _get_report_values(self,docids, data=None):
        report_obj = self.env['sale.margin.report'].browse(docids)
        vals = {
            'doc_ids':docids,
            'doc_model':'sale.margin.report',
            'docs':report_obj,
            'get_sale_order':self.get_sale_order,
            'get_cost':self.get_cost,
            'get_discount':self.get_discount,
            'get_margin':self.get_margin,
            'get_margin_percentage':self.get_margin_percentage,
            'data':data,
        }
        return vals

    def get_sale_order(self,docs):
        domain = [('date_order', '>=', docs.min_date), ('date_order', '<=', docs.max_date), ('state', '!=', 'cancel')]
        if docs.warehouse_ids:
            domain.append(('warehouse_id', 'in', docs.warehouse_ids.ids))
        if docs.product_ids:
            domain.append(('order_line.product_id', 'in', docs.product_ids.ids))
        if docs.order_ids:
            domain.append(('id', 'in', docs.order_ids.ids))
        if docs.partner_ids:
            domain.append(('partner_id', 'in', docs.partner_ids.ids))
        if docs.team_ids:
            domain.append(('team_id', 'in', docs.team_ids.ids))
        if docs.user_ids:
            domain.append(('user_id', 'in', docs.user_ids.ids))
        if docs.company_ids:
            domain.append(('company_id', 'child_of', docs.company_ids.ids))
        sale_orders = self.env['sale.order'].search(domain)
        return sale_orders

    def get_cost(self,line):
        cost = ''
        currency = line.order_id.pricelist_id.currency_id
        if line.purchase_price:
            cost = line.purchase_price * line.product_uom_qty
        else:
            currency = line.order_id.pricelist_id.currency_id
            from_cur = line.env.user.company_id.currency_id.with_context(date=line.order_id.date_order)
            gross_cost = from_cur.compute(line.product_id.standard_price, currency, round=False)
            cost = gross_cost * line.product_uom_qty
        return cost

    def get_discount(self,line):
         discount = round(((line.price_unit * line.product_uom_qty) - line.price_subtotal), 2)
         return discount if discount else ''

    def get_margin(self,line):
        cost = self.get_cost(line)
        margin=round((line.price_subtotal - cost if cost else 0),2)
        return margin

    def get_margin_percentage(self,line):
        margin_per = ''
        margin = self.get_margin(line)
        if margin and line.price_subtotal:
            margin_per = round((margin * 100 / line.price_subtotal), 2)
        return margin_per
