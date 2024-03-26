from odoo import api, fields, models, _
from io import BytesIO
import base64
import datetime
try:
    import xlwt
    from xlwt import Borders
except ImportError:
    xlwt = None

CONTEXT={}

class sale_margin_report(models.TransientModel):
    _name = 'sale.margin.report'

    file_name = fields.Char('File Name', size=50)
    warehouse_ids = fields.Many2many('stock.warehouse','sale_margin_report_warehouse_rel','margin_id','warehouse_id', string='Warehouse')
    product_ids = fields.Many2many('product.product','sale_margin_report_product_product_rel','margin_id','product_id',string='Products')
    order_ids = fields.Many2many('sale.order','sale_margin_report_sale_order_rel','margin_id','order_id',string='Sale Order')
    partner_ids = fields.Many2many('res.partner','sale_margin_report_res_partner_rel','margin_id','partner_id',string='Customers')
    team_ids = fields.Many2many('crm.team','sale_margin_report_crm_team_rel','margin_id','team_id',string='Sales Channel')
    user_ids = fields.Many2many('res.users','sale_margin_report_res_users_rel','margin_id','user_id',string='Salesperson')
    company_ids = fields.Many2many('res.company','sale_margin_report_res_company_rel','margin_id','company_id',string='Company')
    is_negative = fields.Boolean('Negative Margin Highlight')
    min_date = fields.Date('From Date', required=False,default=datetime.date.today().replace(day=1))
    max_date = fields.Date('To Date', required=False, default=fields.Date.today())
    datas = fields.Binary('File')

    #############################################
    # Excel sale margin report data file create #
    #############################################
    def sale_margin_report(self, min_date, max_date, warehouse_ids=False,product_ids=False,order_ids=False,partner_ids=False,team_ids=False,user_ids=False,company_ids=False,is_negative=False):
        column = 0
        row = 5
        workbook = xlwt.Workbook()
        borders = Borders()
        header_border = Borders()
        header_border.left, header_border.right, header_border.top, header_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
        borders.left, borders.right, borders.top, borders.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THIN
        header_bold = xlwt.easyxf("font: bold on, height 240; pattern: pattern solid, fore_colour gray25; alignment: horizontal center ,vertical center")
        date_bold = xlwt.easyxf("font: bold on, height 230; alignment: horizontal left ,vertical center")
        header_style = xlwt.easyxf("font: bold on, height 230; pattern: pattern solid, fore_colour ice_blue; alignment: horizontal center ,vertical center")
        # header_bold.borders = header_border
        header_style.alignment.wrap = 1
        body_style = xlwt.easyxf("font: height 220; alignment: horizontal left")
        body_style.borders = borders
        is_highlight_style = xlwt.easyxf("font: color red, height 220;alignment: horizontal left")
        body_style.borders = borders
        xlwt.add_palette_colour("light_blue_21", 0x21)
        workbook.set_colour_RGB(0x21, 176, 216, 230)
        xlwt.add_palette_colour("custom_orange", 0x22)
        workbook.set_colour_RGB(0x22, 255, 204, 153)
        value_style = xlwt.easyxf("font: height 220,bold on, name Arial; align: horiz right, vert center;    borders: top thin,right thin,bottom thin,left thin")
        is_highlight_value_style = xlwt.easyxf("font: color red,height 220,bold on, name Arial; align: horiz right, vert center; borders: top thin,right thin,bottom thin,left thin")
        xlwt.add_palette_colour("custom_pink", 0x23)
        workbook.set_colour_RGB(0x23, 255, 204, 204)
        worksheet = workbook.add_sheet("Sale Margin Details ", cell_overwrite_ok=True)
        domain=[('date_order', '>=', str(min_date)),('date_order', '<=', str(max_date)),('state', '!=', 'cancel')]
        if warehouse_ids:
            domain.append(('warehouse_id', 'in', warehouse_ids.ids))
        if  product_ids:
            domain.append(('order_line.product_id','in',product_ids.ids))
        if  order_ids:
            domain.append(('id','in',order_ids.ids))
        if  partner_ids:
            domain.append(('partner_id','in',partner_ids.ids))
        if  team_ids:
            domain.append(('team_id','in',team_ids.ids))
        if  user_ids:
            domain.append(('user_id','in',user_ids.ids))
        if  company_ids:
            domain.append(('company_id','child_of',company_ids.ids))
        sale_orders=self.env['sale.order'].search(domain)
        headers = ['Sale Order', 'Product Name', 'Date', 'Customer', 'Warehouse', 'Team', 'Salesperson', 'Company', 'Cost','Untaxed Sale','Discount Amount','Margin Amount','Margin Percentage']
        worksheet.col(0).width = 3000
        worksheet.col(1).width = 7000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5500
        worksheet.col(5).width = 3500
        worksheet.col(6).width = 3500
        worksheet.col(7).width = 3500
        worksheet.col(8).width = 3500
        worksheet.col(9).width = 4000
        worksheet.col(10).width = 4300
        worksheet.col(11).width = 4300
        worksheet.col(12).width = 4300
        worksheet.set_panes_frozen(True)
        worksheet.set_horz_split_pos(5)
        worksheet.set_vert_split_pos(2)
        worksheet.write(0, 0,'From Date:', date_bold)
        worksheet.write(0,1,'%s' % (min_date),date_bold)
        worksheet.write(1, 0,'To Date:', date_bold)
        worksheet.write(1,1,'%s' %(max_date), date_bold)
        worksheet.write_merge(2, 3, 0, 12, 'Sale Margin Report', header_bold)
        for header in headers:
            worksheet.row(4).height = 500
            worksheet.write(4, column, header, header_style)
            column = column + 1
        flag = False
        if sale_orders:
            for so in sale_orders:
                name = so.name
                date_order = str(so.date_order) or ''
                partner_id = so.partner_id and so.partner_id.name or ''
                so_warehouse_id = so.warehouse_id and so.warehouse_id.name or ''
                team  = so.team_id and so.team_id.name or ''
                company = so.company_id and so.company_id.name or ''
                user = so.user_id and so.user_id.name or ''
                for line in so.order_line.filtered(lambda x : x.product_id.id in self.product_ids.ids) if self.product_ids else so.order_line:
                    col = column
                    cost = 0
                    currency = so.pricelist_id.currency_id
                    if line.purchase_price:
                        cost = line.purchase_price * line.product_uom_qty
                    else:
                        currency = line.order_id.pricelist_id.currency_id
                        from_cur = line.env.user.company_id.currency_id.with_context(date=line.order_id.date_order)
                        gross_cost = from_cur.compute(line.product_id.standard_price, currency, round=False)
                        cost = gross_cost * line.product_uom_qty
                    discount = round(((line.price_unit * line.product_uom_qty) - line.price_subtotal), 2)
                    margin = line.price_subtotal - cost
                    margin_per = False
                    if margin and line.price_subtotal:
                        margin_per = margin * 100 / line.price_subtotal
                    worksheet.write(row, 0, name, is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 1, line.product_id and str('%s %s'%(str([line.product_id.default_code]) if line.product_id.default_code else '' ,line.product_id.name)) or '', is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 2, date_order,is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 3, partner_id,is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 4, so_warehouse_id,is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 5, team,is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 6, user,is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 7, company,is_highlight_style if self.is_negative and margin < 0 else body_style)
                    worksheet.write(row, 8, '%s %s'%(str(cost),currency.symbol) if cost else '',is_highlight_value_style if self.is_negative and margin < 0 else value_style)
                    worksheet.write(row, 9, '%s %s'%(str(line.price_subtotal),line.order_id.pricelist_id.currency_id.symbol) if line.price_subtotal else '',is_highlight_value_style if self.is_negative and margin < 0 else value_style)
                    worksheet.write(row, 10, '%s %s' % (str(discount), line.order_id.pricelist_id.currency_id.symbol) if discount else '',is_highlight_value_style if self.is_negative and margin < 0 else value_style)
                    worksheet.write(row, 11, '%s %s'%(str(margin),line.order_id.pricelist_id.currency_id.symbol) if margin else '',is_highlight_value_style if self.is_negative and margin < 0 else value_style)
                    worksheet.write(row, 12, round(margin_per, 2) or '',is_highlight_value_style if self.is_negative and margin < 0 else value_style)
                    flag = True
                    col = col + 1
                    if flag:
                        worksheet.row(row).height = 400
                        row = row + 1
                        flag = False
                    fp = BytesIO()
                    workbook.save(fp)
                    fp.seek(0)
                    report_data_file = base64.encodebytes(fp.read())
        else:
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            report_data_file = base64.encodebytes(fp.read())

        return report_data_file

    ##########################################################
    #print excel report from sale margin report menu in sales#
    ##########################################################

    def print_sale_margin_report(self):
        warehouse_ids = self.warehouse_ids or False
        report_data_file = self.sale_margin_report(self.min_date, self.max_date, warehouse_ids,self.product_ids or False,self.order_ids or False,self.partner_ids or False,self.team_ids or False,self.user_ids or False,self.company_ids or False,self.is_negative or False)
        file_name = 'sale_margin_report' + ".xls"
        self.write({'datas': report_data_file, 'file_name': file_name})
        fp = BytesIO()
        fp.close()
        self.update({'datas': report_data_file})

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=sale.margin.report&field=datas&download=true&id=%s&filename=%s' % (self.id,file_name),
            'target': 'new',
        }

    @api.onchange('company_ids')
    def onchange_company_ids(self):
        domain_filter = {'warehouse_ids':[], 'team_ids':[], 'user_ids':[], 'order_ids':[]}
        if self.company_ids:
            self.warehouse_ids=self.team_ids=self.user_ids=self.order_ids=False
            domain_filter.update({'warehouse_ids':[('company_id', 'child_of', self.company_ids.ids)],
                                  'team_ids':[('company_id', 'child_of', self.company_ids.ids)],
                                  'user_ids':[('company_id', 'child_of', self.company_ids.ids)],
                                  'order_ids':[('company_id', 'child_of', self.company_ids.ids)]
                                  })

        return {'domain':domain_filter}

    @api.onchange('warehouse_ids')
    def onchange_warehouse_ids(self):
        domain_filter = {'order_ids':[('company_id', 'child_of', self.company_ids.ids)]}
        if self.warehouse_ids:
            self.order_ids = False
            domain_filter.update({'order_ids':[('warehouse_id', 'in', self.warehouse_ids.ids)]})
        if not self.warehouse_ids and not self.company_ids:
            self.order_ids =False
            domain_filter.update({'order_ids':[]})

        return {'domain':domain_filter}

    def generate_pdf_report(self):
        CONTEXT.update({'landscape':True,'sale_margin_report':True})
        return self.env.ref('sale_margin_report_ept.sale_margin_report_action').with_context(landscape=True,sale_margin_report=True).report_action(self)  # report_action